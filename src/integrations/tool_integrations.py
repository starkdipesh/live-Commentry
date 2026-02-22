"""
Friday's Professional Tool Integrations
Git helper, IDE assistant, calendar, and notes management.
Integrates with professional tools to provide a complete assistant experience.
"""

import subprocess
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class GitHelper:
    """Git integration for version control assistance."""
    
    def __init__(self, repo_path: Optional[str] = None):
        """Initialize GitHelper with optional repository path."""
        self.repo_path = repo_path or os.getcwd()
        self.last_commit_msg = ""
        self.last_branch = ""
    
    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def get_status(self) -> Dict:
        """Get git repository status."""
        if not self.is_git_repo():
            return {"error": "Not a git repository"}
        
        try:
            # Get status
            status_result = subprocess.run(
                ["git", "-C", self.repo_path, "status", "--short"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Get branch
            branch_result = subprocess.run(
                ["git", "-C", self.repo_path, "branch", "--show-current"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Get recent commits
            log_result = subprocess.run(
                ["git", "-C", self.repo_path, "log", "--oneline", "-5"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                "is_repo": True,
                "branch": branch_result.stdout.strip(),
                "status": status_result.stdout.strip(),
                "has_changes": len(status_result.stdout.strip()) > 0,
                "recent_commits": log_result.stdout.strip().split('\n') if log_result.stdout else [],
                "files_changed": self._parse_status(status_result.stdout)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _parse_status(self, status_output: str) -> List[Dict]:
        """Parse git status output into structured data."""
        files = []
        for line in status_output.strip().split('\n'):
            if line:
                status_code = line[:2]
                filename = line[3:]
                files.append({
                    "status": status_code,
                    "file": filename,
                    "staged": status_code[0] != ' ' and status_code[0] != '?',
                    "unstaged": status_code[1] != ' '
                })
        return files
    
    def generate_commit_message(self, diff_summary: Optional[str] = None) -> str:
        """Generate an AI-like commit message based on changes."""
        status = self.get_status()
        if not status.get("has_changes"):
            return "No changes to commit"
        
        files = status.get("files_changed", [])
        
        # Analyze file patterns
        added_files = [f for f in files if f["status"].startswith('A')]
        modified_files = [f for f in files if 'M' in f["status"]]
        deleted_files = [f for f in files if 'D' in f["status"]]
        
        # Generate message based on patterns
        messages = []
        
        if added_files:
            if any('test' in f["file"].lower() for f in added_files):
                messages.append("Add tests")
            elif any('config' in f["file"].lower() or '.env' in f["file"] for f in added_files):
                messages.append("Add configuration")
            elif any(f["file"].endswith('.md') for f in added_files):
                messages.append("Add documentation")
            else:
                messages.append(f"Add {len(added_files)} new file(s)")
        
        if modified_files:
            if any('fix' in f["file"].lower() or 'bug' in f["file"].lower() for f in modified_files):
                messages.append("Fix bugs")
            elif any('feature' in f["file"].lower() for f in modified_files):
                messages.append("Update features")
            else:
                main_files = [f["file"] for f in modified_files[:3]]
                messages.append(f"Update {', '.join(main_files)}")
        
        if deleted_files:
            messages.append(f"Remove {len(deleted_files)} file(s)")
        
        if not messages:
            messages.append("Update code")
        
        return "; ".join(messages[:2])  # Max 2 parts
    
    def commit(self, message: Optional[str] = None, auto_add: bool = False) -> Dict:
        """Commit changes with optional auto-generated message."""
        if not self.is_git_repo():
            return {"status": "error", "message": "Not a git repository"}
        
        try:
            # Auto-add if requested
            if auto_add:
                subprocess.run(
                    ["git", "-C", self.repo_path, "add", "-A"],
                    capture_output=True,
                    timeout=5
                )
            
            # Generate or use provided message
            commit_msg = message or self.generate_commit_message()
            
            result = subprocess.run(
                ["git", "-C", self.repo_path, "commit", "-m", commit_msg],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.last_commit_msg = commit_msg
                return {
                    "status": "success",
                    "message": commit_msg,
                    "output": result.stdout.strip()
                }
            else:
                return {
                    "status": "error",
                    "message": result.stderr.strip()
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_diff_summary(self) -> str:
        """Get a summary of current changes."""
        if not self.is_git_repo():
            return "Not a git repository"
        
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "diff", "--stat"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout.strip() or "No unstaged changes"
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"
    
    def suggest_commit(self) -> Dict:
        """Get a complete suggestion for committing."""
        if not self.is_git_repo():
            return {"status": "error", "message": "Not a git repository"}
        
        status = self.get_status()
        if not status.get("has_changes"):
            return {"status": "info", "message": "No changes to commit", "suggestion": None}
        
        diff_summary = self.get_diff_summary()
        suggested_msg = self.generate_commit_message()
        
        return {
            "status": "success",
            "has_changes": True,
            "files_changed": len(status.get("files_changed", [])),
            "current_branch": status.get("branch"),
            "diff_summary": diff_summary,
            "suggested_message": suggested_msg,
            "suggestion": f"git add -A && git commit -m '{suggested_msg}'"
        }


class IDEAssistant:
    """IDE integration for development assistance."""
    
    def __init__(self):
        """Initialize IDEAssistant."""
        self.supported_editors = ["code", "cursor", "zed", "idea", "pycharm", "subl"]
    
    def detect_open_editor(self) -> Optional[str]:
        """Detect which IDE/editor is currently open."""
        # Check for common editors
        try:
            result = subprocess.run(
                ["xdotool", "search", "--class", "code"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                return "VS Code"
        except:
            pass
        
        try:
            result = subprocess.run(
                ["xdotool", "search", "--class", "jetbrains"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                return "JetBrains IDE"
        except:
            pass
        
        return None
    
    def get_recent_projects(self) -> List[str]:
        """Get list of recent projects from VS Code history."""
        try:
            # VS Code stores recent folders in global storage
            vscode_state_path = Path.home() / ".config" / "Code" / "Global Storage" / "state.vscdb"
            if vscode_state_path.exists():
                # This is a SQLite DB, would need proper parsing
                return ["Recent projects available (parse VS Code DB for details)"]
        except:
            pass
        
        return []
    
    def open_project(self, project_path: str) -> Dict:
        """Open a project in the default IDE."""
        try:
            # Try VS Code first
            result = subprocess.run(
                ["code", project_path],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": f"Opened {project_path} in VS Code"
                }
            else:
                # Fallback to xdg-open
                subprocess.run(
                    ["xdg-open", project_path],
                    capture_output=True,
                    timeout=10
                )
                return {
                    "status": "success",
                    "message": f"Opened {project_path} in default application"
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}


class NotesManager:
    """Notes and knowledge management integration."""
    
    def __init__(self, notes_dir: Optional[str] = None):
        """Initialize NotesManager."""
        if notes_dir is None:
            self.notes_dir = Path.home() / "FridayNotes"
        else:
            self.notes_dir = Path(notes_dir)
        
        self.notes_dir.mkdir(parents=True, exist_ok=True)
    
    def create_note(self, title: str, content: str, category: str = "general") -> Dict:
        """Create a new note."""
        try:
            # Sanitize filename
            safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{safe_title}.md"
            
            category_dir = self.notes_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = category_dir / filename
            
            # Write note with metadata
            note_content = f"""# {title}

**Created:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Category:** {category}

---

{content}

---

*Captured by Friday*
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(note_content)
            
            return {
                "status": "success",
                "filepath": str(filepath),
                "title": title
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def search_notes(self, query: str) -> List[Dict]:
        """Search notes by content."""
        results = []
        
        try:
            for md_file in self.notes_dir.rglob("*.md"):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            # Extract title
                            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                            title = title_match.group(1) if title_match else md_file.stem
                            
                            results.append({
                                "title": title,
                                "filepath": str(md_file),
                                "snippet": content[:200] + "..."
                            })
                except:
                    continue
        except Exception as e:
            print(f"Search error: {e}")
        
        return results
    
    def get_recent_notes(self, n: int = 5) -> List[Dict]:
        """Get n most recent notes."""
        try:
            notes = []
            for md_file in self.notes_dir.rglob("*.md"):
                stat = md_file.stat()
                notes.append({
                    "filepath": str(md_file),
                    "modified": stat.st_mtime,
                    "filename": md_file.name
                })
            
            # Sort by modification time
            notes.sort(key=lambda x: x["modified"], reverse=True)
            
            # Get titles
            result = []
            for note in notes[:n]:
                try:
                    with open(note["filepath"], 'r') as f:
                        content = f.read()
                        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                        title = title_match.group(1) if title_match else note["filename"]
                        result.append({
                            "title": title,
                            "filepath": note["filepath"]
                        })
                except:
                    continue
            
            return result
        except:
            return []


class CalendarHelper:
    """Calendar integration for time management."""
    
    def __init__(self):
        """Initialize CalendarHelper."""
        self.events_cache = []
        self.last_fetch = 0
    
    def get_upcoming_events(self, hours_ahead: int = 24) -> List[Dict]:
        """
        Get upcoming calendar events.
        
        Note: This is a placeholder. Real implementation would integrate with:
        - Google Calendar API
        - Microsoft Outlook
        - Local calendar (ical)
        """
        # Placeholder implementation
        return []
    
    def check_meeting_soon(self, minutes: int = 10) -> Optional[Dict]:
        """Check if there's a meeting starting soon."""
        events = self.get_upcoming_events(hours_ahead=1)
        now = datetime.now()
        
        for event in events:
            event_time = event.get("start_time")
            if event_time:
                diff = (event_time - now).total_seconds() / 60
                if 0 < diff <= minutes:
                    return event
        
        return None
    
    def suggest_daily_prep(self) -> Dict:
        """Suggest morning preparation based on calendar."""
        events = self.get_upcoming_events(hours_ahead=8)
        
        if not events:
            return {
                "has_meetings": False,
                "suggestion": "No meetings scheduled today. Good day for focused work, Sir."
            }
        
        meeting_count = len(events)
        first_meeting = events[0]
        
        return {
            "has_meetings": True,
            "meeting_count": meeting_count,
            "first_meeting": first_meeting.get("title"),
            "first_meeting_time": first_meeting.get("start_time"),
            "suggestion": f"You have {meeting_count} meetings today. First one: {first_meeting.get('title')}"
        }


class ToolIntegrations:
    """
    Unified interface for all professional tool integrations.
    Provides a single access point for Git, IDE, Notes, and Calendar.
    """
    
    def __init__(self):
        """Initialize all tool integrations."""
        self.git = GitHelper()
        self.ide = IDEAssistant()
        self.notes = NotesManager()
        self.calendar = CalendarHelper()
    
    def get_context_summary(self) -> Dict:
        """Get a summary of current development context."""
        summary = {
            "git": None,
            "ide": None,
            "meetings": None
        }
        
        # Git context
        if self.git.is_git_repo():
            git_status = self.git.get_status()
            summary["git"] = {
                "is_repo": True,
                "branch": git_status.get("branch"),
                "has_changes": git_status.get("has_changes"),
                "files_changed": len(git_status.get("files_changed", []))
            }
        
        # IDE context
        open_ide = self.ide.detect_open_editor()
        if open_ide:
            summary["ide"] = {"editor": open_ide}
        
        # Meeting context
        upcoming = self.calendar.check_meeting_soon(minutes=30)
        if upcoming:
            summary["meetings"] = {
                "meeting_soon": True,
                "title": upcoming.get("title"),
                "minutes_until": int((upcoming.get("start_time") - datetime.now()).total_seconds() / 60)
            }
        
        return summary
    
    def execute_command(self, command_type: str, params: Dict) -> Dict:
        """
        Execute a tool integration command.
        
        Args:
            command_type: Type of command (git, notes, ide, calendar)
            params: Command parameters
            
        Returns:
            Command result
        """
        if command_type == "git":
            action = params.get("action")
            if action == "status":
                return self.git.get_status()
            elif action == "commit":
                return self.git.commit(
                    message=params.get("message"),
                    auto_add=params.get("auto_add", False)
                )
            elif action == "suggest":
                return self.git.suggest_commit()
            elif action == "diff":
                return {"summary": self.git.get_diff_summary()}
        
        elif command_type == "notes":
            action = params.get("action")
            if action == "create":
                return self.notes.create_note(
                    title=params.get("title"),
                    content=params.get("content"),
                    category=params.get("category", "general")
                )
            elif action == "search":
                return {"results": self.notes.search_notes(params.get("query", ""))}
            elif action == "recent":
                return {"notes": self.notes.get_recent_notes(params.get("n", 5))}
        
        elif command_type == "ide":
            action = params.get("action")
            if action == "open_project":
                return self.ide.open_project(params.get("path"))
            elif action == "detect":
                return {"editor": self.ide.detect_open_editor()}
        
        return {"status": "error", "message": f"Unknown command: {command_type}"}


# Convenience functions
def quick_commit(message: Optional[str] = None) -> Dict:
    """Quick helper to commit changes."""
    git = GitHelper()
    return git.commit(message=message, auto_add=True)


def quick_note(title: str, content: str) -> Dict:
    """Quick helper to create a note."""
    notes = NotesManager()
    return notes.create_note(title, content)
