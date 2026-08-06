import argparse
import json
import os
import sys
import threading
import urllib.parse
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingTCPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from topic_manager import TopicManager
from import_favs import import_from_favs
from archive_topics import archive_completed_topics


class ThreadedTCPServer(ThreadingTCPServer):
    allow_reuse_address = True


class TopicRequestHandler(SimpleHTTPRequestHandler):
    db_path = None
    web_dir = None

    def __init__(self, *args, **kwargs):
        web_directory = str(self.web_dir) if self.web_dir else str(BASE_DIR / "web")
        super().__init__(*args, directory=web_directory, **kwargs)

    def _send_json(self, data, status_code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, message, status_code=400):
        self._send_json({"error": message}, status_code=status_code)

    def _read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            body_bytes = self.rfile.read(content_length)
            return json.loads(body_bytes.decode("utf-8"))
        return {}

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/topics":
            query = urllib.parse.parse_qs(parsed.query)
            status = query.get("status", [None])[0]
            category = query.get("category", [None])[0]

            tm = TopicManager(data_file=self.db_path)
            topics = tm.get_all(status=status, category=category)
            self._send_json(topics, status_code=200)
            return

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/topics":
            try:
                payload = self._read_json_body()
            except Exception as e:
                self._send_error(f"Invalid JSON body: {e}", status_code=400)
                return

            title = payload.get("title")
            if not title:
                self._send_error("Title is required", status_code=400)
                return

            tm = TopicManager(data_file=self.db_path)
            try:
                topic = tm.add(
                    title=title,
                    category=payload.get("category", ""),
                    hook=payload.get("hook", ""),
                    source_platform=payload.get("source_platform", ""),
                    source_title=payload.get("source_title", ""),
                    source_url=payload.get("source_url", ""),
                    angles=payload.get("angles"),
                    outline=payload.get("outline"),
                    tags=payload.get("tags"),
                    status=payload.get("status", "inbox"),
                )
                self._send_json(topic, status_code=201)
            except ValueError as e:
                self._send_error(str(e), status_code=400)
            return

        elif path == "/api/topics/sync":
            try:
                payload = self._read_json_body()
            except Exception as e:
                self._send_error(f"Invalid JSON body: {e}", status_code=400)
                return

            if isinstance(payload, list):
                tm = TopicManager(data_file=self.db_path)
                tm.save_all(payload)
                self._send_json({"success": True, "count": len(payload)}, status_code=200)
            else:
                self._send_error("Expected list of topics", status_code=400)
            return

        elif path == "/api/import-favs":
            try:
                payload = self._read_json_body()
            except Exception:
                payload = {}

            favs_path = payload.get("favs_path")
            imported_count = import_from_favs(favs_path=favs_path, db_path=self.db_path)
            self._send_json({"imported": imported_count}, status_code=200)
            return

        elif path == "/api/topics/archive":
            try:
                payload = self._read_json_body()
            except Exception:
                payload = {}

            days = payload.get("days", 30)
            archive_path = payload.get("archive_path")
            archived_count = archive_completed_topics(days=days, db_path=self.db_path, archive_path=archive_path)
            self._send_json({"archived": archived_count}, status_code=200)
            return

        self._send_error("Not Found", status_code=404)

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/topics/"):
            topic_id = path[len("/api/topics/"):]
            try:
                payload = self._read_json_body()
            except Exception as e:
                self._send_error(f"Invalid JSON body: {e}", status_code=400)
                return

            tm = TopicManager(data_file=self.db_path)
            try:
                updated = tm.update(topic_id, payload)
                self._send_json(updated, status_code=200)
            except KeyError as e:
                self._send_error(str(e), status_code=404)
            except ValueError as e:
                self._send_error(str(e), status_code=400)
            return

        self._send_error("Not Found", status_code=404)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/topics/"):
            topic_id = path[len("/api/topics/"):]
            tm = TopicManager(data_file=self.db_path)
            try:
                tm.delete(topic_id)
                self._send_json({"success": True}, status_code=200)
            except KeyError as e:
                self._send_error(str(e), status_code=404)
            return

        self._send_error("Not Found", status_code=404)


def create_handler_class(db_path=None, web_dir=None):
    if web_dir is None:
        web_dir = BASE_DIR / "web"
    web_dir = Path(web_dir)
    web_dir.mkdir(parents=True, exist_ok=True)

    class CustomTopicRequestHandler(TopicRequestHandler):
        pass

    CustomTopicRequestHandler.db_path = db_path
    CustomTopicRequestHandler.web_dir = web_dir
    return CustomTopicRequestHandler


def run_server(port=18922, db_path=None, web_dir=None, block=True):
    handler_class = create_handler_class(db_path=db_path, web_dir=web_dir)
    server = ThreadedTCPServer(("0.0.0.0", port), handler_class)
    if block:
        try:
            print(f"Starting server on http://127.0.0.1:{server.server_address[1]}")
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            server.server_close()
        return server
    else:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server


def main():
    parser = argparse.ArgumentParser(description="esheep-topic-master REST API & Static Server")
    parser.add_argument("--port", type=int, default=18922, help="Port to listen on")
    parser.add_argument("--db-path", default=None, help="Path to topics.json")
    parser.add_argument("--web-dir", default=None, help="Path to web static files directory")

    args = parser.parse_args()
    run_server(port=args.port, db_path=args.db_path, web_dir=args.web_dir, block=True)


if __name__ == "__main__":
    main()
