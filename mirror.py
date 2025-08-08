import logging
import threading
import requests
import time
import os
import glob
import shutil
import configtony
from pathlib import Path
from backupchan import API, BackupTarget, Backup, BackupchanAPIError

class Mirror:
    def __init__(self, main_config: configtony.Config, target_config: configtony.Config):
        self.logger = logging.getLogger(__name__)
        self.check_interval = main_config.get("check_interval")
        self.save_path = main_config.get("save_path")
        self.api = API(main_config.get("connection")["host"], main_config.get("connection")["port"], main_config.get("connection")["apikey"])
        self.targets = target_config.get("targets")
    
    def start(self):
        self.logger.info("Start mirror process")
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        while True:
            self.mirror()
            time.sleep(self.check_interval)

    def mirror(self):
        for target_id in self.targets:
            self.logger.info("Begin mirroring target: {%s}", target_id)
            target, backups = self.safe_get_target(target_id)
            if target is None:
                continue

            checked_backups = set()
            recycled_backups = set()

            target_save_path = self.target_save_path(target_id)
            Path(target_save_path).mkdir(parents=True, exist_ok=True)
            for backup in backups:
                if backup.is_recycled:
                    recycled_backups.add(backup.id)
                    self.logger.info("Backup {%s} is recycled", backup.id)
                    continue

                checked_backups.add(backup.id)
                if self.has_backup(backup):
                    self.logger.info("Already have backup {%s}", backup.id)
                else:
                    self.logger.info("Downloading backup {%s}", backup.id)
                    download_path = self.api.download_backup(backup.id, target_save_path)
                    _, extension = os.path.splitext(download_path)
                    final_path = self.backup_save_path(target_id, backup.id) + extension
                    shutil.move(download_path, final_path)
                    self.logger.info("Saved to: %s", final_path)

            self.logger.info("Running cleanup")
            self.cleanup(target_id, checked_backups, recycled_backups)
            self.logger.info("Target {%s} successfully mirrored.", target_id)
            
        self.logger.info("Finished mirroring")

    def cleanup(self, target_id: str, checked_backups: set[str], recycled_backups: set[str]):
        target_path = self.target_save_path(target_id)
        for file_path in glob.glob(os.path.join(target_path, "*")):
            backup_id = Path(file_path).stem
            if backup_id not in checked_backups or backup_id in recycled_backups:
                self.logger.info("Deleting backup {%s} not present on server or recycled", backup_id)
                try:
                    os.remove(file_path)
                except OSError as exc:
                    self.logger.error("Failed to delete file %s: %s", file_path, exc)

    def target_save_path(self, target_id: str) -> str:
        return os.path.join(self.save_path, target_id)

    def backup_save_path(self, target_id: str, backup_id: str) -> str:
        return os.path.join(self.target_save_path(target_id), backup_id)

    def has_backup(self, backup: Backup) -> bool:
        backup_save_path = self.backup_save_path(backup.target_id, backup.id)
        return os.path.exists(backup_save_path) or bool(glob.glob(backup_save_path + ".*"))

    def safe_get_target(self, target_id: str) -> tuple[BackupTarget | None, list[Backup] | None]:
        while True:
            try:
                return self.api.get_target(target_id)
            except requests.exceptions.ConnectionError as exc:
                self.logger.error("Network error when accessing target {%s}", target_id, exc_info=exc)
            except BackupchanAPIError as exc:
                self.logger.error("Error when accessing target {%s}: %s", target_id, str(exc))
                return None, None
