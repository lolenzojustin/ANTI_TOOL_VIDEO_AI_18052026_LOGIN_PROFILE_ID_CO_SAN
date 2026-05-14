import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import requests

# Import các file phụ trợ
from tool_video_ai_layout_3_UI import Ui_Widget
from GpmGlobalApi_tuviet import Gpm

class MultiThread(QThread):
    # Khai báo signal trả về: (Số thứ tự cảnh, trạng thái, dữ liệu N8N trả về)
    record = pyqtSignal(int, str, str)

    def __init__(self, index, api_n8n, api_url_gpm):
        super().__init__()
        self.index = index
        self.api_n8n = api_n8n
        self.api_url_gpm = api_url_gpm  # URL GPM lấy từ giao diện
        self.is_running = True

    def run(self):
        gpm = Gpm()
        profile_id = None
        
        try:
            # 1. Tạo Profile GPM mới
            self.record.emit(self.index, "Đang tạo profile GPM", "-")
            profile_id = gpm.create_profile_2(apiurl_Gpm=self.api_url_gpm)
            
            # 2. Mở Profile GPM
            self.record.emit(self.index, "Đang mở GPM", "-")
            remote_addr = gpm.open_profile(apiurl_Gpm=self.api_url_gpm, id_profile=profile_id)
            
            # Kiểm tra kết quả open_profile
            if not remote_addr:
                raise RuntimeError("open_profile trả về None — GPM chưa khởi động hoặc API URL GPM sai.")
            
            # 3. Kéo Playwright vào điều khiển trình duyệt
            self.record.emit(self.index, "Đang chạy Playwright", "-")
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(f"http://{remote_addr}")
                context = browser.contexts[0]
                # Lấy tab mặc định hoặc tạo tab mới
                page = context.pages[0] if context.pages else context.new_page()
                
                # Mở google và nhập "test cảnh"
                page.goto("https://www.google.com")
                # Chọn thẻ input search của Google
                search_input = page.locator('textarea[name="q"], input[name="q"]').first
                search_input.wait_for(state="visible", timeout=15000)
                search_input.fill("test cảnh")
                page.keyboard.press("Enter")
                
                # Đợi một lát để trang load kết quả
                page.wait_for_timeout(3000) 
                
                # 4. Call API N8N
                self.record.emit(self.index, "Đang gọi API N8N", "-")
                payload = {
                    "scene_index": self.index,
                    "action": "Tìm kiếm google: test cảnh"
                }
                
                response = requests.post(
                    self.api_n8n,
                    json=payload,
                    timeout=120
                )
                
                try:
                    result = response.json()
                except Exception:
                    result = response.text
                
                # Báo cáo hoàn thành và gửi kết quả
                self.record.emit(self.index, "Hoàn thành", str(result)[:200])
                
                browser.close()
                
        except Exception as e:
            import traceback
            print(f"[Cảnh {self.index}] EXCEPTION:\n{traceback.format_exc()}")
            self.record.emit(self.index, f"Lỗi: {e}", "-")
        finally:
            # 5. Dọn dẹp: Đóng và xóa profile GPM rác sau khi làm xong
            if profile_id:
                # Bước 5a: Đóng trình duyệt GPM
                try:
                    gpm.close_profile(apiurl_Gpm=self.api_url_gpm, id_profile=profile_id)
                    print(f"[Cảnh {self.index}] ✅ Đã close_profile: {profile_id}")
                except Exception as e:
                    print(f"[Cảnh {self.index}] ⚠️ close_profile thất bại: {e}")

                # Bước 5b: Xóa profile ra khỏi GPM
                try:
                    gpm.delete_profile(apiurl_Gpm=self.api_url_gpm, id_profile=profile_id)
                    print(f"[Cảnh {self.index}] ✅ Đã delete_profile: {profile_id}")
                except Exception as e:
                    print(f"[Cảnh {self.index}] ⚠️ delete_profile thất bại: {e}")

    def stop(self):
        self.is_running = False

class Manager(QtWidgets.QMainWindow, Ui_Widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.threads = []
        self.completed_threads = 0
        self.total_threads = 0

        # Kết nối sự kiện Click cho nút "BẮT ĐẦU TẠO VIDEO" bên tab Veo3
        self.veo3_btn_analyze.clicked.connect(self.startThreadVeo3)

    def startThreadVeo3(self):
        # Kiểm tra xem có luồng nào đang chạy dở không
        if any(t.isRunning() for t in self.threads):
            QMessageBox.warning(self, "Đang chạy", "Vui lòng chờ các tiến trình cũ hoàn thành.")
            return

        # Lấy số lượng "cảnh" (số luồng) từ combobox giao diện góc trái
        try:
            input_soluong = int(self.cb_scene_count.currentText())
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Số lượng cảnh không hợp lệ.")
            return

        # Lấy API URL GPM từ ô nhập liệu trên giao diện
        input_api_url_gpm = self.le_api_url_gpm.text().strip()
        if not input_api_url_gpm:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập API URL GPM (ví dụ: http://localhost:9495).")
            return

        input_api_n8n = "https://leminhthang.io.vn/webhook/5be66201-0ab3-4244-b6f7-2182dd3eee91"

        self.total_threads = input_soluong
        self.completed_threads = 0
        
        # Cập nhật số tiến trình trên nút Đang xử lý
        self.veo3_btn_running.setText(f"⏱ Đang xử lý... 0/{self.total_threads}")

        self.threads = []

        # Khởi tạo GPM theo đúng số "cảnh" đã chọn
        for i in range(1, input_soluong + 1):
            thread = MultiThread(
                index=i,
                api_n8n=input_api_n8n,
                api_url_gpm=input_api_url_gpm  # Truyền URL GPM từ giao diện
            )

            # Lắng nghe dữ liệu bắn về từ Thread để update log
            thread.record.connect(self.update_data)
            self.threads.append(thread)
            thread.start()
            
            # Delay 1.5 giây giữa các luồng để tránh spam API GPM và treo máy
            time.sleep(1.5)

    def update_data(self, index, status, response_data):
        # In log ra màn hình console để theo dõi
        print(f"[Cảnh {index}] Trạng thái: {status} | Phản hồi N8N: {response_data}")
        
        # Nếu luồng hoàn tất hoặc bị lỗi, tăng bộ đếm lên 1
        if status == "Hoàn thành" or status.startswith("Lỗi"):
            self.completed_threads += 1
            # Cập nhật hiển thị (vd: "⏱ Đang xử lý... 3/10")
            self.veo3_btn_running.setText(f"⏱ Đang xử lý... {self.completed_threads}/{self.total_threads}")
            
            # Nếu tất cả các luồng đã xong
            if self.completed_threads == self.total_threads:
                QMessageBox.information(self, "Thành công", f"Đã chạy xong toàn bộ {self.total_threads} cảnh!")

    def closeEvent(self, event):
        # Stop và dọn dẹp các Thread khi ấn X tắt phần mềm
        for t in self.threads:
            t.stop()
            t.wait(1000)
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Manager()
    window.showMaximized()
    sys.exit(app.exec_())