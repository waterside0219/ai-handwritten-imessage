"""WebDriverAgent 的小客户端：只留这件事用得上的几个动作。

环境变量：
  WDA_URL   直接给地址，例如 http://[fd00::1]:8100
  WDA_UDID  不给 WDA_URL 时，用 `xcrun devicectl` 按这个 UDID 找 USB 隧道地址

命令行：
  python3 wda.py status | session <bundleId> | shot <out.png> | source <out.xml>
  python3 wda.py tap <x> <y> | click <accessibility id> | type <文字> | url <scheme://...>
  python3 wda.py orientation LANDSCAPE|PORTRAIT | drag <x1> <y1> <x2> <y2>
"""
import base64
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

STATE = Path(__file__).with_name(".wda-session")
_base = None


def base_url():
    global _base
    if _base:
        return _base
    if os.environ.get("WDA_URL"):
        _base = os.environ["WDA_URL"].rstrip("/")
        return _base
    udid = os.environ.get("WDA_UDID")
    if not udid:
        raise SystemExit("set WDA_URL or WDA_UDID")
    out = Path(tempfile.gettempdir()) / "wda-devices.json"
    subprocess.run(["xcrun", "devicectl", "list", "devices", "--json-output", str(out)], capture_output=True)
    for device in json.loads(out.read_text())["result"]["devices"]:
        if device["hardwareProperties"].get("udid") == udid:
            _base = f"http://[{device['connectionProperties']['tunnelIPAddress']}]:8100"
            return _base
    raise SystemExit("device not found; is it plugged in and unlocked?")


def req(method, path, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(base_url() + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=timeout) as response:
            return json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as error:
        try:
            return json.loads(error.read() or b"{}")
        except Exception:
            return {"value": {"error": str(error)}}


def sid():
    return STATE.read_text().strip()


def session(bundle_id):
    r = req("POST", "/session", {"capabilities": {"alwaysMatch": {
        "bundleId": bundle_id, "shouldWaitForQuiescence": False}}})
    STATE.write_text(r["sessionId"])
    return r["sessionId"]


def screenshot(path):
    Path(path).write_bytes(base64.b64decode(req("GET", "/screenshot")["value"]))


def source():
    return req("GET", f"/session/{sid()}/source")["value"]


def pointer(actions):
    """W3C actions：一根手指的一串动作。"""
    return req("POST", f"/session/{sid()}/actions", {"actions": [{
        "type": "pointer", "id": "finger", "parameters": {"pointerType": "touch"}, "actions": actions}]})


def tap(x, y):
    return pointer([{"type": "pointerMove", "duration": 0, "x": x, "y": y},
                    {"type": "pointerDown", "button": 0}, {"type": "pause", "duration": 80},
                    {"type": "pointerUp", "button": 0}])


def click(accessibility_id):
    value = req("POST", f"/session/{sid()}/element",
                {"using": "accessibility id", "value": accessibility_id}).get("value", {})
    element = value.get("ELEMENT") or value.get("element-6066-11e4-a52e-4f735466cecc")
    if not element:
        return False
    req("POST", f"/session/{sid()}/element/{element}/click")
    return True


def type_text(text):
    return req("POST", f"/session/{sid()}/wda/keys", {"value": list(text)})


def open_url(url):
    return req("POST", f"/session/{sid()}/url", {"url": url}, timeout=20)


def orientation(value):
    return req("POST", f"/session/{sid()}/orientation", {"orientation": value}, timeout=20)


def drag(x1, y1, x2, y2, seconds=0.4):
    return req("POST", f"/session/{sid()}/wda/dragfromtoforduration",
               {"fromX": x1, "fromY": y1, "toX": x2, "toY": y2, "duration": seconds})


def main():
    cmd, *a = sys.argv[1:]
    if cmd == "status":
        print(req("GET", "/status")["value"].get("ready"))
    elif cmd == "session":
        print(session(a[0]))
    elif cmd == "shot":
        screenshot(a[0]); print("ok")
    elif cmd == "source":
        Path(a[0]).write_text(source()); print("ok")
    elif cmd == "tap":
        tap(float(a[0]), float(a[1])); print("ok")
    elif cmd == "click":
        print("ok" if click(a[0]) else "not found")
    elif cmd == "type":
        type_text(a[0]); print("ok")
    elif cmd == "url":
        open_url(a[0]); print("ok")
    elif cmd == "orientation":
        orientation(a[0]); print("ok")
    elif cmd == "drag":
        drag(*map(float, a[:4])); print("ok")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
