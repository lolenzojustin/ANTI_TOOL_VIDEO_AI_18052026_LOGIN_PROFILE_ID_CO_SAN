import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import os
import time
import threading
import requests


# Import các file phụ trợ
from tool_video_ai_layout_3_UI import Ui_Widget
from GpmGlobalApi_tuviet import Gpm

class MultiThread(QThread):
    # Khai báo signal trả về: (Số thứ tự cảnh, trạng thái, kết quả)
    record = pyqtSignal(int, str, str)

    def __init__(self, index, api_url_gpm, profile_id="", prompt_text="test cảnh", win_size="800,800", win_pos="0,0"):
        super().__init__()
        self.index = index
        self.api_url_gpm = api_url_gpm  # URL GPM lấy từ giao diện
        self.profile_id = profile_id    # ID Profile cho luồng này
        self.prompt_text = prompt_text
        self.win_size = win_size
        self.win_pos = win_pos
        self.is_running = True
        self._stop_event = threading.Event()  # Event để dừng sleep ngay lập tức

    def run(self):
        gpm = Gpm()
        profile_id = self.profile_id
        
        status = None
        response_data = "-"
        try:
            # 1. Kiểm tra ID Profile GPM
            if not self.is_running:
                status = "Đã dừng"
                return
            if not profile_id:
                raise RuntimeError("Chưa có ID Profile cho cảnh này.")
            
            # 2. Mở Profile GPM
            if not self.is_running:
                status = "Đã dừng"
                return
            self.record.emit(self.index, "Đang mở GPM", "-")
            remote_addr = gpm.open_profile(apiurl_Gpm=self.api_url_gpm, id_profile=profile_id, win_pos=self.win_pos, win_size=self.win_size)
            
            # Kiểm tra kết quả open_profile
            if not remote_addr:
                raise RuntimeError("open_profile trả về None — GPM chưa khởi động hoặc API URL GPM sai.")
            
            # 3. Kéo Playwright vào điều khiển trình duyệt
            if not self.is_running:
                status = "Đã dừng"
                return
            self.record.emit(self.index, "Đang chạy Playwright", "-")
            with sync_playwright() as p:
                browser = None
                for attempt in range(5):
                    try:
                        browser = p.chromium.connect_over_cdp(f"http://{remote_addr}")
                        break
                    except Exception as e:
                        print(f"[Cảnh {self.index}] Lỗi kết nối CDP (lần {attempt+1}), thử lại sau 2s...")
                        time.sleep(2)
                if not browser:
                    raise RuntimeError("Không thể kết nối Playwright với trình duyệt.")
                
                context = browser.contexts[0]
                # Lấy tab mặc định hoặc tạo tab mới
                page = context.pages[0] if context.pages else context.new_page()
                
                # Áp dụng cứng viewport size cho Playwright để hiển thị chính xác
                try:
                    w, h = map(int, self.win_size.split(","))
                    page.set_viewport_size({"width": w, "height": h})
                except Exception:
                    pass
                
                # Bước 1: vào trang https://labs.google/fx/vi/tools/flow
                try:
                    page.goto("https://labs.google/fx/vi/tools/flow", timeout=60000, wait_until="domcontentloaded")
                except PlaywrightTimeoutError:
                    print(f"[Cảnh {self.index}] goto timeout, tiếp tục...")
                
                # Kiểm tra dừng sau khi goto
                if not self.is_running:
                    browser.close()
                    status = "Đã dừng"
                    return
                
                # Bước 2: Đợi load xong trang thì Bấm Dự án mới
                try:
                    new_project_btn = page.locator('[data-type="button-overlay"]').first
                    new_project_btn.wait_for(state="visible", timeout=15000)
                    new_project_btn.click()
                    print(f"[Cảnh {self.index}] Đã bấm Dự án mới.")
                except Exception as e:
                    print(f"[Cảnh {self.index}] Lỗi khi bấm Dự án mới: {e}")
                
                # Kiểm tra dừng
                if not self.is_running:
                    browser.close()
                    status = "Đã dừng"
                    return
                
                # Xử lý popup thông báo cookie nếu có (giữ nguyên cấu trúc xử lý popup chung)
                try:
                    close_btn = page.locator('button[aria-label="Close"], button[aria-label="Đóng"], [role="dialog"] button:has(svg)').first
                    close_btn.wait_for(state="visible", timeout=3000)
                    close_btn.click()
                    print(f"[Cảnh {self.index}] Đã đóng popup thông báo.")
                except PlaywrightTimeoutError:
                    pass
                except Exception:
                    pass
                
                # Bước 3: Sau khi bấm Dự án mới load xong thì gõ vào prompt của dự án đó
                search_input = page.locator('textarea:visible, div[contenteditable="true"]:visible').last
                search_input.wait_for(state="visible", timeout=15000)
                search_input.click()
                page.keyboard.type(self.prompt_text)
                
                # Bước 4: Sau khi gõ prompt xong thì đợi 10 giây là xong 1 luồng chứ ko bấm nút enter
                time.sleep(10)
                
                # Sau khi xong, đánh dấu hoàn thành và đóng browser
                status = "Hoàn thành"
                print(f"[Cảnh {self.index}] ✅ Đã gõ prompt xong và đợi 10s, chuẩn bị đóng browser")
                browser.close()
                
        except Exception as e:
            import traceback
            print(f"[Cảnh {self.index}] EXCEPTION:\n{traceback.format_exc()}")
            status = f"Lỗi: {e}"
            response_data = "-"
        finally:
            # 5. Dọn dẹp: Đóng profile GPM sau khi làm xong
            if profile_id:
                self._cleanup_profile(gpm, profile_id)
            
            if status:
                self.record.emit(self.index, status, response_data)

    def _cleanup_profile(self, gpm, profile_id):
        close_attempts = 3
        close_success = False
        for attempt in range(1, close_attempts + 1):
            try:
                response = gpm.close_profile(apiurl_Gpm=self.api_url_gpm, id_profile=profile_id)
                if isinstance(response, dict) and response.get("success") is False:
                    raise RuntimeError(f"close_profile trả về lỗi: {response}")
                print(f"[Cảnh {self.index}] ✅ Đã close_profile: {profile_id} (lần {attempt})")
                close_success = True
                break
            except Exception as e:
                print(f"[Cảnh {self.index}] ⚠️ close_profile thất bại lần {attempt}: {e}")
                time.sleep(2)
        if not close_success:
            print(f"[Cảnh {self.index}] ⚠️ close_profile không thành công sau {close_attempts} lần.")
        return True

    def stop(self):
        """Ra hiệu dừng: đặt cả boolean lẫn Event để ngắt sleep ngay lập tức."""
        self.is_running = False
        self._stop_event.set()  # Ngắt bất kỳ _stop_event.wait() nào đang bị block

class PromptApiThread(QThread):
    finished = pyqtSignal()
    prompt_result = pyqtSignal(int, str)

    def __init__(self, urls, payload, post_url):
        super().__init__()
        self.urls = urls
        self.payload = payload
        self.post_url = post_url

    def run(self):
        # 1. Gọi API POST để gửi thông tin lên N8N
        try:
            print(f"[Phân tích Prompt] Đang gọi API POST: {self.post_url}")
            response_post = requests.post(self.post_url, json=self.payload, timeout=60)
            print(f"[Phân tích Prompt] Đã gửi POST thành công - Status: {response_post.status_code}")
        except Exception as e:
            print(f"[Phân tích Prompt] Lỗi gọi API POST N8N: {e}")

        # 2. Gọi các API GET theo số lượng cảnh để nhận kết quả cho giao diện
        for index, url in enumerate(self.urls, start=1):
            try:
                print(f"[Phân tích Prompt] Đang gọi API GET {index}: {url}")
                response = requests.get(url, timeout=15)
                
                try:
                    data = response.json()
                    content = data.get("content", "")
                    if content:
                        self.prompt_result.emit(index, content)
                except ValueError:
                    print(f"[Phân tích Prompt] Không thể parse JSON từ API GET {index}")

                print(f"[Phân tích Prompt] Hoàn thành API GET {index} - Status: {response.status_code}")
            except Exception as e:
                print(f"[Phân tích Prompt] Lỗi gọi API GET {index}: {e}")
                
        self.finished.emit()

class Manager(QtWidgets.QMainWindow, Ui_Widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.config = {}  # Dictionary để lưu config values không phải widget
        self.config_path = os.path.join(os.path.dirname(__file__), "config.env")
        self._config_map = {
            "AI_MODEL": self.cb_ai_model,
            "ASYNC_API_KEY": self.le_api_key,
            "API_URL_GPM": self.le_api_url_gpm,
            "BROWSER": self.cb_browser,
            "WIN_SIZE": self.cb_win_size,
            "VIDEO_FOLDER": self.le_folder,
            "STYLE": self.cb_style,
            "LANGUAGE": self.cb_language,
            "COPY_RATIO": self.cb_copy_ratio,
            "SCENE_COUNT": self.cb_scene_count,
            "VOICE_DESC": self.te_voice_desc,
            "PROXY_LIST": self.te_proxy_input,
            "GROK_LANG": self.grok_cb_lang,
            "GROK_LINK": self.grok_le_link,
            "GROK_DESC": self.grok_le_desc,
            "VEO3_LANG": self.veo3_cb_lang,
            "VEO3_LINK": self.veo3_le_link,
            "VEO3_DESC": self.veo3_le_desc,
            "SEED_LANG": self.seed_cb_lang,
            "SEED_LINK": self.seed_le_link,
            "SEED_DESC": self.seed_le_desc,
            "KOL_LANG": self.kol_cb_lang,
            "KOL_DESC": self.kol_le_desc,
            "KOL_PROMPT": self.kol_le_prompt,
        }

        self._load_config()
        self.scene_prompt_boxes = self.tab_veo3.findChildren(QtWidgets.QTextEdit, "promptBox")
        self._connect_config_signals()

        self.threads = []
        self.completed_threads = 0
        self.total_threads = 0
        self.running_threads = 0    # Số luồng đang chạy thực tế
        self._is_stopping = False   # Flag để bỏ qua signal của thread khi đã bấm dừng

        # Kết nối nút proxy: mở rộng / thu gọn bảng nhập proxy
        self.btn_proxy_collapsed.clicked.connect(self._toggle_proxy_panel)
        self.btn_proxy_close.clicked.connect(self._toggle_proxy_panel)

        # Danh sách webhook API
        self.WEBHOOK_URLS = [
            "https://thangdepzai.devttt.com/webhook/11ca20ab-5425-48b7-8aa2-7b517597f196",
            "https://thangdepzai.devttt.com/webhook/81a25e7e-6f7b-4d96-9e40-45130a5e3ab7",
            "https://thangdepzai.devttt.com/webhook/c4dc4bc4-fd95-485d-b638-c9957d6abd0f",
            "https://thangdepzai.devttt.com/webhook/69fb1066-09b2-40a5-8b02-a5a33c682aa0",
            "https://thangdepzai.devttt.com/webhook/120fc52b-9b7e-4bcc-a1cd-e6fdcca457c1",
            "https://thangdepzai.devttt.com/webhook/ee39526e-7f92-4c56-a32e-bd0c0f336009",
            "https://thangdepzai.devttt.com/webhook/cbc9be64-6fff-4579-83d2-1ba3ce2d079b",
            "https://thangdepzai.devttt.com/webhook/b8887c04-04f0-4857-b4cb-9d307335f88c",
            "https://thangdepzai.devttt.com/webhook/ad1d5232-e771-4bee-891a-1b751ef90858",
            "https://thangdepzai.devttt.com/webhook/3534d74c-722b-4f71-9db7-5fa62614c818"
        ]
        self.prompt_thread = None

        # Kết nối sự kiện Click cho nút "BẮT ĐẦU TẠO VIDEO" bên tab Veo3
        self.veo3_btn_analyze.clicked.connect(self.startThreadVeo3)
        
        # Kết nối sự kiện Click cho nút "Bắt đầu phân tích tạo Prompt" cho cả 2 tab
        self.veo3_btn_merge.clicked.connect(self.analyzePrompts)
        self.kol_btn_merge.clicked.connect(self.analyzePrompts)
        
        # Kết nối nút cập nhật phiên bản cho cả hai tab
        self.veo3_btn_update.clicked.connect(self._update_version)
        self.kol_btn_update.clicked.connect(self._update_version)

    def _set_veo3_btn_running(self, is_running):
        """Đổi trạng thái nút BẮT ĐẦU TẠO VIDEO theo trạng thái luồng."""
        if is_running:
            self.veo3_btn_analyze.setText("⏹  ĐANG CHẠY TẠO VIDEO...BẤM ĐỂ DỪNG CHẠY")
            self.veo3_btn_analyze.setStyleSheet(
                "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                " stop:0 #b91c1c, stop:1 #f97316);"
                " border: none; color: white; font-weight: bold;"
            )
        else:
            self.veo3_btn_analyze.setText("🚀  Bắt đầu tạo video từ tất cả cảnh")
            # Xoá style inline → fallback về QSS gốc (#analyzeBtn)
            self.veo3_btn_analyze.setStyleSheet("")

    def _stop_all_veo3_threads(self):
        """Dừng tất cả luồng đang chạy và reset UI ngay lập tức."""
        self._is_stopping = True  # Báo hiệu cho update_data bỏ qua signal từ giờ này
        for t in self.threads:
            t.stop()
        print("[Manager] ⛔ Đã gửi lệnh dừng tất cả luồng.")
        # Reset UI ngay lập tức — không chờ thread kết thúc
        self.running_threads = 0
        self.completed_threads = self.total_threads  # Đánh dấu đã xong để tránh lệch counter
        self.veo3_btn_running.setText("⏱ Đang xử lý 0 luồng")
        self._set_veo3_btn_running(False)
        QtWidgets.QApplication.processEvents()  # Buộc UI render ngay

    def _set_prompt_btn_running(self, is_running):
        """Đổi trạng thái nút Bắt đầu phân tích tạo Prompt."""
        if is_running:
            text = "⏳ Đang phân tích tạo prompt..."
            style = (
                "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                " stop:0 #9333ea, stop:1 #d8b4fe);"
                " border: none; color: white; font-weight: bold;"
            )
            self.veo3_btn_merge.setText(text)
            self.veo3_btn_merge.setStyleSheet(style)
            self.kol_btn_merge.setText(text)
            self.kol_btn_merge.setStyleSheet(style)
        else:
            text = "🎬 Bắt đầu phân tích tạo Prompt"
            self.veo3_btn_merge.setText(text)
            self.veo3_btn_merge.setStyleSheet("")
            self.kol_btn_merge.setText(text)
            self.kol_btn_merge.setStyleSheet("")

    def analyzePrompts(self):
        try:
            input_soluong = int(self.cb_scene_count.currentText())
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Số lượng cảnh không hợp lệ.")
            return

        if input_soluong <= 0:
            return

        # Khởi chạy thread để call API không làm đơ UI
        if self.prompt_thread and self.prompt_thread.isRunning():
            QMessageBox.warning(self, "Cảnh báo", "Đang phân tích tạo prompt, vui lòng đợi!")
            return

        urls_to_call = self.WEBHOOK_URLS[:input_soluong]
        api_url = "https://n8n.aiplt.io.vn/webhook/webhook_get_data_tool"
        print(f"[Manager] Bắt đầu gọi {len(urls_to_call)} API (GET) và 1 API POST...")
        self._set_prompt_btn_running(True)
        QtWidgets.QApplication.processEvents()

        # Thu thập 8 thông tin từ UI
        payload = {
            "link_youtube": self.veo3_le_link.text().strip() if hasattr(self, 'veo3_le_link') else "",
            "mo_ta_them": self.veo3_le_desc.text().strip() if hasattr(self, 'veo3_le_desc') else "",
            "mo_hinh_sinh_kich_ban": self.cb_ai_model.currentText(),
            "asynclab_api_key": self.le_api_key.text().strip(),
            "phong_cach": self.cb_style.currentText(),
            "ngon_ngu": self.cb_language.currentText(),
            "ty_le_copy": self.cb_copy_ratio.currentText(),
            "giong_nhan_vat": self.te_voice_desc.toPlainText().strip(),
            "so_canh": input_soluong
        }

        self.prompt_thread = PromptApiThread(urls_to_call, payload, api_url)
        self.prompt_thread.prompt_result.connect(self._on_prompt_result)
        self.prompt_thread.finished.connect(self._on_prompt_thread_finished)
        self.prompt_thread.start()

    def _on_prompt_result(self, index, content):
        """Cập nhật dữ liệu prompt nhận được từ API lên textbox của cảnh tương ứng."""
        if 1 <= index <= len(self.scene_prompt_boxes):
            self.scene_prompt_boxes[index - 1].setPlainText(content)

    def _on_prompt_thread_finished(self):
        self._set_prompt_btn_running(False)
        QMessageBox.information(self, "Thành công", "Đã hoàn thành gửi yêu cầu phân tích tạo Prompt!")

    def startThreadVeo3(self):
        # Nếu đang có luồng chạy → bấm nút = dừng tất cả
        if any(t.isRunning() for t in self.threads):
            self._stop_all_veo3_threads()
            return

        # Reset flag dừng trước mỗi lần chạy mới
        self._is_stopping = False

        # Lấy số lượng "cảnh" (số luồng) từ combobox giao diện góc trái
        try:
            input_soluong = int(self.cb_scene_count.currentText())
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Số lượng cảnh không hợp lệ.")
            return

        # Giới hạn tối đa 10 luồng
        if input_soluong > 10:
            QMessageBox.warning(self, "Lỗi", "Số lượng cảnh tối đa là 10.")
            return

        # Lấy API URL GPM từ ô nhập liệu trên giao diện
        input_api_url_gpm = self.le_api_url_gpm.text().strip()
        if not input_api_url_gpm:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập API URL GPM (ví dụ: http://localhost:9495).")
            return

        # Đọc danh sách Profile ID từ ô nhập thủ công trên giao diện
        # Giữ nguyên vị trí từng dòng: luồng i lấy ID dòng i
        profile_id_list = []
        proxy_text = self.te_proxy_input.toPlainText().strip()
        if proxy_text:
            for line in proxy_text.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    profile_id_list.append("")
                else:
                    profile_id_list.append(line)
        valid_count = sum(1 for p in profile_id_list if p)
        print(f"[Manager] Đọc được {valid_count}/{len(profile_id_list)} ID Profile.")

        # Kiểm tra số lượng Profile và định dạng Profile ID
        invalid_profile_format = any(
            p and not re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", p)
            for p in profile_id_list
        )
        if valid_count < input_soluong or invalid_profile_format:
            QMessageBox.warning(
                self,
                "Kiểm tra lại danh sách Profile",
                "Vui lòng kiểm tra lại danh sách Profile. Số Profile đang ít hơn số cảnh hoặc định dạng điền trong danh sách Profile không đúng"
            )
            return

        self.total_threads = input_soluong
        self.completed_threads = 0
        self.running_threads = input_soluong  # Khởi đầu: tất cả luồng đều chạy
        
        # Cập nhật nút Đang xử lý: hiển thị số luồng đang chạy
        self.veo3_btn_running.setText(f"⏱ Đang xử lý {self.running_threads} luồng")

        # Đổi nút sang trạng thái đang chạy NGAY lập tức trước khi khởi động luồng
        self._set_veo3_btn_running(True)
        QtWidgets.QApplication.processEvents()  # Buộc UI render ngay

        self.threads = []

        input_win_size_raw = self.cb_win_size.currentText()
        input_win_size = input_win_size_raw.replace("px", "").replace(":", ",")
        
        try:
            win_w, win_h = map(int, input_win_size.split(","))
        except:
            win_w, win_h = 800, 800

        # Lấy kích thước màn hình
        screen_rect = QtWidgets.QApplication.desktop().screenGeometry()
        screen_width = screen_rect.width()
        cols = max(1, screen_width // win_w)

        # Khởi tạo GPM theo đúng số "cảnh" đã chọn
        for i in range(1, input_soluong + 1):
            # Lấy Profile ID theo index (dòng i-1 trong ô nhập)
            profile_id = profile_id_list[i - 1] if (i - 1) < len(profile_id_list) else ""
            
            # Tính toán vị trí hiển thị luồng
            idx = i - 1
            col = idx % cols
            row = idx // cols
            pos_x = col * win_w
            pos_y = row * win_h
            win_pos = f"{pos_x},{pos_y}"
            
            # Lấy nội dung prompt hiển thị trên giao diện của cảnh tương ứng
            current_prompt = "test cảnh"
            if (i - 1) < len(self.scene_prompt_boxes):
                text = self.scene_prompt_boxes[i - 1].toPlainText().strip()
                if text:
                    current_prompt = text
                    
            thread = MultiThread(
                index=i,
                api_url_gpm=input_api_url_gpm,
                profile_id=profile_id,
                prompt_text=current_prompt,
                win_size=input_win_size,
                win_pos=win_pos
            )

            # Lắng nghe dữ liệu bắn về từ Thread để update log
            thread.record.connect(self.update_data)
            self.threads.append(thread)
            thread.start()
            
            # Delay 1.5 giây giữa các luồng để tránh spam API GPM và treo máy
            time.sleep(1.5)

    def update_data(self, index, status, response_data):
        # Nếu đang trong trạng thái dừng thủ công → bỏ qua tín hiệu từ thread
        if self._is_stopping:
            print(f"[Cảnh {index}] Bỏ qua signal (tool đã dừng): {status}")
            return

        # In log ra màn hình console để theo dõi
        print(f"[Cảnh {index}] Trạng thái: {status} | Phản hồi N8N: {response_data}")
        
        # Nếu luồng hoàn tất, bị lỗi, hoặc bị dừng thì giảm bộ đếm luồng đang chạy
        if status == "Hoàn thành" or status.startswith("Lỗi") or status == "Đã dừng":
            if status == "Hoàn thành" and response_data:
                # Cập nhật text prompt cho cảnh tương ứng nếu có dữ liệu trả về
                if 1 <= index <= len(self.scene_prompt_boxes):
                    self.scene_prompt_boxes[index - 1].setPlainText(response_data)

            self.completed_threads += 1
            self.running_threads = max(0, self.running_threads - 1)  # Giảm luồng đang chạy
            # Cập nhật nút hiển thị số luồng đang chạy
            self.veo3_btn_running.setText(f"⏱ Đang xử lý {self.running_threads} luồng")
            
            # Nếu tất cả các luồng đã xong (hoàn thành / lỗi / dừng)
            if self.completed_threads == self.total_threads:
                self.running_threads = 0
                self.veo3_btn_running.setText("⏱ Đang xử lý 0 luồng")
                # Trả text nút về trạng thái ban đầu
                self._set_veo3_btn_running(False)
                if status != "Đã dừng":  # Chỉ thông báo "Thành công" nếu không phải dừng thủ công
                    QMessageBox.information(self, "Thành công", f"Đã chạy xong toàn bộ {self.total_threads} cảnh!")

    def _connect_config_signals(self):
        for widget in self._config_map.values():
            if isinstance(widget, QtWidgets.QComboBox):
                widget.currentTextChanged.connect(self._save_config)
            elif isinstance(widget, QtWidgets.QLineEdit):
                widget.textChanged.connect(self._save_config)
            elif isinstance(widget, QtWidgets.QTextEdit):
                widget.textChanged.connect(self._save_config)
        self.tabWidget.currentChanged.connect(self._save_config)

    def _load_config(self):
        values = self._read_env_file()
        for key, widget in self._config_map.items():
            if key not in values:
                continue
            value = self._decode_env_value(values[key])
            if isinstance(widget, QtWidgets.QComboBox):
                idx = widget.findText(value)
                if idx >= 0:
                    widget.setCurrentIndex(idx)
            elif isinstance(widget, QtWidgets.QTextEdit):
                widget.setPlainText(value)
            else:
                widget.setText(value)

        # Load version từ config
        if "VERSION" in values:
            self.config["VERSION"] = self._decode_env_value(values["VERSION"])
        else:
            self.config["VERSION"] = "1.0"

        if "CURRENT_TAB" in values:
            try:
                tab_index = int(values["CURRENT_TAB"])
                if 0 <= tab_index < self.tabWidget.count():
                    self.tabWidget.setCurrentIndex(tab_index)
            except ValueError:
                pass

        self._save_config()

    def _read_env_file(self):
        if not os.path.exists(self.config_path):
            return {}
        data = {}
        with open(self.config_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                data[key.strip()] = val.strip()
        return data

    def _decode_env_value(self, value):
        return value.replace("\\n", "\n")

    def _encode_env_value(self, value):
        return value.replace("\n", "\\n")

    def _save_config(self):
        env_data = {}
        for key, widget in self._config_map.items():
            if isinstance(widget, QtWidgets.QComboBox):
                env_data[key] = widget.currentText()
            elif isinstance(widget, QtWidgets.QTextEdit):
                env_data[key] = widget.toPlainText()
            else:
                env_data[key] = widget.text()
        
        # Lưu VERSION từ config dictionary
        env_data["VERSION"] = self.config.get("VERSION", "1.0")
        env_data["CURRENT_TAB"] = str(self.tabWidget.currentIndex())

        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write("# Auto-generated config for tool UI values\n")
            for key, value in env_data.items():
                f.write(f"{key}={self._encode_env_value(value)}\n")

    def _toggle_proxy_panel(self):
        """Thu gọn hoặc mở rộng bảng nhập Profile."""
        is_expanded = self.proxy_expand_panel.isVisible()
        if is_expanded:
            # Đóng panel → cập nhật text nút thu gọn
            self.proxy_expand_panel.setVisible(False)
            count = sum(
                1 for line in self.te_proxy_input.toPlainText().splitlines()
                if line.strip() and not line.strip().startswith("#")
            )
            if count:
                self.btn_proxy_collapsed.setText(f"📋  {count} Profile — Nhấp để chỉnh sửa")
            else:
                self.btn_proxy_collapsed.setText("📋  Nhấp để nhập danh sách Profile")
        else:
            # Mở panel
            self.proxy_expand_panel.setVisible(True)

    def _update_version(self):
        """Cho phép người dùng cập nhật phiên bản tool."""
        from PyQt5 import QtWidgets
        
        # Danh sách phiên bản có sẵn
        available_versions = ["1.0", "1.1", "1.2", "1.3"]
        
        # Lấy phiên bản hiện tại từ config
        current_version = self.config.get("VERSION", "1.0")
        
        # Tìm index của phiên bản hiện tại
        current_index = available_versions.index(current_version) if current_version in available_versions else 0
        
        # Hiển thị dialog chọn phiên bản
        selected_version, ok = QtWidgets.QInputDialog.getItem(
            self, 
            "Cập nhật phiên bản", 
            "Chọn phiên bản:",
            available_versions,
            current_index,
            editable=False
        )
        
        if ok and selected_version.strip():
            # Cập nhật config
            self.config["VERSION"] = selected_version.strip()
            
            # Cập nhật UI trên cả hai tab
            # Tìm tất cả QLabel với objectName "verLabel" và cập nhật text
            for widget in self.findChildren(QtWidgets.QLabel):
                if widget.objectName() == "verLabel":
                    widget.setText(f"Phiên bản {selected_version.strip()}")
            
            # Lưu config vào file
            self._save_config()

    def closeEvent(self, event):
        # Stop và dọn dẹp các Thread khi ấn X tắt phần mềm
        for t in self.threads:
            t.stop()
            if not t.wait(5000):
                print(f"[Manager] Thread {t.index} vẫn đang chạy khi đóng ứng dụng.")
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Manager()
    window.resize(1920, 1245)
    window.show()
    sys.exit(app.exec_())