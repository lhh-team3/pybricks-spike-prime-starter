"""
Wrapper script to run pybricksdev and handle SystemExit properly.
This ensures the debugger session terminates when the robot program stops.
"""
import sys
import subprocess
import os


def main():
    # Build pybricksdev command
    args = [sys.executable, "-m", "pybricksdev"] + sys.argv[1:]

    try:
        # Start pybricksdev process with unbuffered output
        # Use UTF-8 encoding to handle progress bar characters
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,  # Unbuffered
            encoding="utf-8",
            errors="replace",  # Replace undecodable characters instead of crashing
        )

        system_exit_detected = False

        # Read output line by line
        while True:
            line = process.stdout.readline()

            if line:
                # Print immediately for real-time output
                print(line, end="", flush=True)

                # Check for SystemExit message - look for either pattern
                if "SystemExit" in line or "was stopped" in line:
                    system_exit_detected = True
                    # Give it a moment to finish any remaining output
                    import time

                    time.sleep(0.3)

                    # Read any remaining output
                    remaining = []
                    process.stdout.flush()
                    while True:
                        try:
                            # Non-blocking read attempt
                            import select

                            if hasattr(select, "select"):
                                # Unix-like systems
                                readable, _, _ = select.select(
                                    [process.stdout], [], [], 0.1
                                )
                                if readable:
                                    extra = process.stdout.readline()
                                    if extra:
                                        remaining.append(extra)
                                    else:
                                        break
                                else:
                                    break
                            else:
                                # Windows - just try to read with a short timeout
                                break
                        except:
                            break

                    # Print any remaining output
                    for r in remaining:
                        print(r, end="", flush=True)

                    # Terminate the process
                    process.terminate()
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()

                    print(
                        "\n[Wrapper] Program terminated on robot, stopping debugger.",
                        flush=True,
                    )
                    sys.exit(0)

            # Check if process has ended
            retcode = process.poll()
            if retcode is not None:
                # Process ended, read any remaining output
                remaining = process.stdout.read()
                if remaining:
                    print(remaining, end="", flush=True)

                if system_exit_detected:
                    print(
                        "\n[Wrapper] Program terminated on robot, stopping debugger.",
                        flush=True,
                    )

                sys.exit(retcode if retcode == 0 or system_exit_detected else retcode)

    except KeyboardInterrupt:
        print("\n[Wrapper] Interrupted by user", flush=True)
        if "process" in locals():
            process.terminate()
        sys.exit(130)
    except Exception as e:
        print(f"[Wrapper] Error running pybricksdev: {e}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
