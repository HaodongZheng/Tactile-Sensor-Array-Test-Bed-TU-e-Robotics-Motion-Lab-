import serial
import time
import math


class NewIndenter:
    def __init__(self, printer_port='COM9', baudrate_printer=115200):
        self.ser = serial.Serial(
            printer_port,
            baudrate_printer,
            timeout=1,
            write_timeout=1,
            rtscts=False,
            dsrdtr=False,
            xonxoff=False,
        )

        # GRBL reset/wakeup
        time.sleep(2)
        self.ser.write(b"\r\n\r\n")
        self.ser.flush()
        time.sleep(2)

        self._read_available("startup")

        self.send_gcode("G21")   # mm units
        self.send_gcode("G90")   # absolute positioning

    def _read_available(self, tag="serial"):
        while self.ser.in_waiting:
            line = self.ser.readline().decode("latin1", errors="replace").strip()
            if line:
                print(f"[{tag}]", repr(line))

    def send_gcode(self, command, wait=True):
        command = command.strip()
        payload = (command + "\r\n").encode("ascii", errors="strict")

        print(">>", repr(payload))
        self.ser.write(payload)
        self.ser.flush()

        if wait:
            self._wait_for_ok(command)

    def _wait_for_ok(self, command, max_empty_reads=10):
        empty_reads = 0

        while True:
            raw = self.ser.readline()

            if not raw:
                empty_reads += 1
                if empty_reads >= max_empty_reads:
                    raise TimeoutError(f"No response after command: {command}")
                continue

            line = raw.decode("latin1", errors="replace").strip()

            if not line:
                continue

            print("[Controller]", repr(line))

            lower = line.lower()

            if lower.startswith("ok"):
                return

            if "error" in lower:
                raise RuntimeError(f"GRBL error after command {command!r}: {line!r}")

            if "alarm" in lower:
                raise RuntimeError(f"GRBL alarm after command {command!r}: {line!r}")


    def _readline_clean(self):
        raw = self.ser.readline()
        if not raw:
            return None
        line = raw.decode("latin1", errors="replace").strip()
        return line if line else None


    def _read_status_once(self, timeout=1.0):
        """
        Send GRBL real-time status query '?' and return the next proper
        status report line, ignoring ok/error/other text.
        """
        t0 = time.time()

        # Important: GRBL real-time command is '?' without newline.
        self.ser.write(b"?")
        self.ser.flush()

        while time.time() - t0 < timeout:
            line = self._readline_clean()
            if not line:
                continue

            print("[RX]", repr(line))

            if line.startswith("<") and line.endswith(">"):
                return line

            if "error" in line.lower():
                raise RuntimeError(f"GRBL error while reading status: {line!r}")

            if "alarm" in line.lower():
                raise RuntimeError(f"GRBL alarm while reading status: {line!r}")

            # Ignore normal "ok" or other messages.

        raise TimeoutError("No GRBL status response received")


    def _parse_state(self, status):
        # Example: <Run|MPos:1.000,2.000,3.000|FS:100,0>
        return status.strip("<>").split("|", 1)[0]


    def _parse_mpos(self, status):
        fields = status.strip("<>").split("|")
        for field in fields:
            if field.startswith("MPos:"):
                return tuple(float(v) for v in field[5:].split(","))
        return None


    def _parse_wpos(self, status):
        fields = status.strip("<>").split("|")
        for field in fields:
            if field.startswith("WPos:"):
                return tuple(float(v) for v in field[5:].split(","))
        return None


    def _parse_feed(self, status):
        fields = status.strip("<>").split("|")
        for field in fields:
            if field.startswith("FS:"):
                # FS:feed,spindle
                return float(field[3:].split(",")[0])
        return None

    def wait_until_idle(self, poll_dt=0.1, min_wait=0.25):
        """
        Wait until motion is really finished.

        Logic:
        1. Wait a short time after command acceptance, so the planner has time
        to transition into Run.
        2. Poll status.
        3. Prefer seeing Run/Jog first.
        4. Only return on Idle after motion has been observed.
        5. If Run is missed, require position and feed to remain stable.
        """
        time.sleep(min_wait)

        saw_motion_state = False
        last_pos = None
        stable_count = 0
        required_stable_count = 4
        stable_eps = 1e-4

        while True:
            status = self._read_status_once()
            state = self._parse_state(status)
            pos = self._parse_mpos(status) or self._parse_wpos(status)
            feed = self._parse_feed(status)

            print("[Status]", repr(status), "state =", state, "pos =", pos, "feed =", feed)

            if state in ("Run", "Jog", "Hold"):
                saw_motion_state = True
                stable_count = 0

            if pos is not None and last_pos is not None:
                diff = math.sqrt(sum((a - b) ** 2 for a, b in zip(pos, last_pos)))

                if diff < stable_eps:
                    stable_count += 1
                else:
                    stable_count = 0

            if pos is not None:
                last_pos = pos

            feed_is_zero = feed is None or abs(feed) < 1e-6

            if state == "Idle":
                if saw_motion_state and feed_is_zero:
                    return

                # Fallback for cases where polling missed the Run state.
                if stable_count >= required_stable_count and feed_is_zero:
                    return

            if state in ("Alarm", "Door", "Check"):
                raise RuntimeError(f"Controller is not in normal motion state: {status!r}")

            time.sleep(poll_dt)

    def set_current_position_as_origin(self):
        self.send_gcode("G92 X0 Y0 Z0")

    def move_to(self, x=None, y=None, z=None, feedrate=1000):
        cmd = "G1"

        if x is not None:
            x = self._check_number(x, "x")
            cmd += f" X{x:.4f}"

        if y is not None:
            y = self._check_number(y, "y")
            cmd += f" Y{y:.4f}"

        if z is not None:
            z = self._check_number(z, "z")
            cmd += f" Z{z:.4f}"

        feedrate = self._check_number(feedrate, "feedrate")
        cmd += f" F{feedrate:.1f}"

        self.send_gcode(cmd)
        self.wait_until_idle()

    def _check_number(self, value, name):
        value = float(value)
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite, got {value}")
        return value

    def close(self):
        self.ser.close()

if __name__ == "__main__":
    ####### Example usage #######
    # If you are using windows, change the port accordingly to "COM"+"X", where X is the port number. 
    INDENTER_PORT = "/dev/ttyUSB0"
    indenter = NewIndenter(INDENTER_PORT, 115200)
    # Set the current position as origin. Do this before you started your experiment.
    indenter.set_current_position_as_origin()
    # Move command example below, I put it to move to (0, 0, 0), so it will stay at where it is, be careful before you change the value.
    # The unit length here is in millimeter
    indenter.move_to(x=0, y=0, z=0, feedrate=1000) 
    indenter.close()
