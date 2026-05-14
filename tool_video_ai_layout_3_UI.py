# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets

# File giao diện để như này:
# from PyQt5 import QtCore, QtGui, QtWidgets
# def _get_scale():
#     ...

# def _s(v, sc):
#     ...

# class Ui_Widget(object):
#     def setupUi(self, Widget):
#         ...

# File chạy chính chỉ cần import:

# from ui_gpm_regsep_14052026 import Ui_Widget
# Không cần import thêm:
# from ui_gpm_regsep_14052026 import _s, _get_scale
def _get_scale():
    app = QtWidgets.QApplication.instance()
    if app is None:
        return 1.0
    screen = app.primaryScreen()
    geom = screen.availableGeometry()
    w, h = geom.width(), geom.height()
    dpi = screen.logicalDotsPerInch()
    dpi_scale = dpi / 96.0
    res_scale = min(w / 1366.0, h / 768.0)
    scale = dpi_scale * max(res_scale, 0.95)
    return max(1.0, min(scale, 1.4))


def _s(v, sc):
    return max(1, int(v * sc))


class Ui_Widget(object):
    def setupUi(self, Widget):
        self._sc = _get_scale()
        sc = self._sc

        Widget.setObjectName("Widget")
        Widget.resize(_s(1500, sc), _s(920, sc))

        self.centralwidget = QtWidgets.QWidget(Widget)
        Widget.setCentralWidget(self.centralwidget)

        root = QtWidgets.QHBoxLayout(self.centralwidget)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── LEFT PANEL ──
        self.leftPanel = QtWidgets.QFrame()
        self.leftPanel.setObjectName("leftPanel")
        self.leftPanel.setFixedWidth(_s(280, sc))

        leftScroll = QtWidgets.QScrollArea()
        leftScroll.setWidgetResizable(True)
        leftScroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        leftBox = QtWidgets.QWidget()
        leftBox.setObjectName("leftBox")
        lv = QtWidgets.QVBoxLayout(leftBox)
        lv.setContentsMargins(_s(4,sc), _s(6,sc), _s(4,sc), _s(6,sc))
        lv.setSpacing(_s(4,sc))

        # Mô hình sinh kịch bản
        lv.addWidget(self._lbl("Mô hình sinh kịch bản", "grpLabel"))
        self.cb_ai_model = self._combo(["Gemini 3.1 Flash Lite", "Gemini 2.0 Flash", "GPT-4o", "Claude 3.5 Sonnet"])
        row1 = self._lbl_save_row(self.cb_ai_model, "btn_save_model")
        lv.addLayout(row1)

        # AsyncLab API Key
        lv.addWidget(self._lbl("AsyncLab API Key", "grpLabel"))
        self.le_api_key = self._le("Nhập AsyncLab Key...", password=True)
        row2 = self._lbl_save_row(self.le_api_key, "btn_save_api")
        lv.addLayout(row2)

        # API URL GPM
        lv.addWidget(self._lbl("API URL GPM", "grpLabel"))
        self.le_api_url_gpm = self._le("http://localhost:1234/api/v1/...")
        row_gpm = self._lbl_save_row(self.le_api_url_gpm, "btn_save_gpm")
        lv.addLayout(row_gpm)

        # Phiên bản trình duyệt
        lv.addWidget(self._lbl("Phiên bản trình duyệt", "grpLabel"))
        self.cb_browser = self._combo(["GPM", "GoLogin", "Chrome", "Firefox", "Edge", "Brave"])
        lv.addWidget(self.cb_browser)

        # File đường dẫn Proxy
        lv.addWidget(self._lbl("File đường dẫn Proxy", "grpLabel"))
        proxy_row = QtWidgets.QHBoxLayout()
        proxy_row.setSpacing(_s(5, sc))
        self.le_proxy_file = self._le("Chọn file proxy (.txt)...")
        self.le_proxy_file.setReadOnly(True)
        btn_proxy_browse = QtWidgets.QPushButton("📂")
        btn_proxy_browse.setObjectName("proxyBrowseBtn")
        btn_proxy_browse.setFixedSize(_s(32, sc), _s(26, sc))
        btn_proxy_browse.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_proxy_browse = btn_proxy_browse
        proxy_row.addWidget(self.le_proxy_file, 1)
        proxy_row.addWidget(btn_proxy_browse)
        lv.addLayout(proxy_row)

        # Đường dẫn folder
        lv.addWidget(self._lbl("Đường dẫn folder lấy video", "grpLabel"))
        self.le_folder = self._le("C:\\Users\\Admin\\Desktop\\VIDEO AI")
        row3 = self._lbl_save_row(self.le_folder, "btn_save_folder")
        lv.addLayout(row3)

        # Mở thư mục
        self.btn_open_folder = QtWidgets.QPushButton("🗂  Mở thư mục xuất này")
        self.btn_open_folder.setObjectName("openFolderBtn")
        self.btn_open_folder.setFixedHeight(_s(40, sc))
        lv.addWidget(self.btn_open_folder)

        self.lb_output = QtWidgets.QLabel("Output: C:\\Users\\Admin\\Desktop\\VIDEO AI")
        self.lb_output.setObjectName("smallBlue")
        self.lb_output.setWordWrap(True)
        lv.addWidget(self.lb_output)

        lv.addWidget(self._hline())

        # TÙY CHỌN KỊCH BẢN
        lv.addWidget(self._lbl("TÙY CHỌN KỊCH BẢN", "sectionTitle"))

        lv.addWidget(self._lbl("Phong cách hình ảnh/video", "grpLabel"))
        self.cb_style = self._combo(["Hyper Realistic (Chân thực 100%)", "Anime Style", "Cinematic", "Cartoon"])
        lv.addWidget(self.cb_style)
        lbl_note_style = self._lbl("* Dùng cho nội dung lịch sử, chân dung", "noteLabel")
        lbl_note_style.setWordWrap(True)
        lv.addWidget(lbl_note_style)

        lv.addWidget(self._lbl("Ngôn từ kịch bản và giọng nói", "grpLabel"))
        self.cb_language = self._combo(["us English", "Tiếng Việt", "Japanese", "Korean"])
        lv.addWidget(self.cb_language)

        lv.addWidget(self._lbl("Tỷ lệ copy từ video gốc", "grpLabel"))
        self.cb_copy_ratio = self._combo(["50% - Copy một nửa", "100% - Copy hoàn toàn", "75%", "25%", "0% - Tự do"])
        lv.addWidget(self.cb_copy_ratio)
        lbl_note_ratio = self._lbl("Copy X% nội dung video gốc, phần còn lại sáng tạo từ cấu trúc và thông điệp gốc", "noteLabel")
        lbl_note_ratio.setWordWrap(True)
        lv.addWidget(lbl_note_ratio)

        lv.addWidget(self._lbl("Số cảnh", "grpLabel"))
        self.cb_scene_count = QtWidgets.QComboBox()
        self.cb_scene_count.addItems([str(i) for i in range(1, 21)])
        self.cb_scene_count.setCurrentIndex(9)  # mặc định = 10
        self.cb_scene_count.setFixedHeight(_s(26, sc))
        lv.addWidget(self.cb_scene_count)

        self.lb_duration_inline = QtWidgets.QLabel("Thời gian: 80 giây")
        self.lb_duration_inline.setObjectName("durationInline")
        lv.addWidget(self.lb_duration_inline)

        lbl_note2 = self._lbl("Tự động tính: 1 cảnh = 8 giây", "noteLabel")
        lbl_note2.setWordWrap(True)
        lv.addWidget(lbl_note2)

        # Kết nối tự cập nhật thời lượng khi đổi số cảnh
        self.cb_scene_count.currentIndexChanged.connect(
            lambda idx: self.lb_duration_inline.setText(f"Thời gian: {(idx + 1) * 8} giây")
        )

        lv.addWidget(self._lbl("Giọng nhân vật đồng nhất", "grpLabel"))
        self.te_voice_desc = QtWidgets.QTextEdit()
        self.te_voice_desc.setPlaceholderText("Nhập mô tả giọng nhân vật...")
        self.te_voice_desc.setObjectName("voiceDesc")
        self.te_voice_desc.setMinimumHeight(_s(100, sc))
        lv.addWidget(self.te_voice_desc)

        lv.addStretch()

        leftScroll.setWidget(leftBox)
        leftWrap = QtWidgets.QVBoxLayout(self.leftPanel)
        leftWrap.setContentsMargins(0, 0, 0, 0)
        leftWrap.addWidget(leftScroll)

        # ── RIGHT PANEL ──
        self.rightPanel = QtWidgets.QFrame()
        self.rightPanel.setObjectName("rightPanel")
        rv = QtWidgets.QVBoxLayout(self.rightPanel)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(0)

        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setDocumentMode(True)

        self.tab_grok     = QtWidgets.QWidget()
        self.tab_veo3     = QtWidgets.QWidget()
        self.tab_seedance = QtWidgets.QWidget()
        self.tab_kol      = QtWidgets.QWidget()

        self._build_tab_content(self.tab_grok,     "grok")
        self._build_tab_content(self.tab_veo3,     "veo3")
        self._build_tab_content(self.tab_seedance, "seed")
        self._build_kol_tab(self.tab_kol)

        self.tabWidget.addTab(self.tab_grok,     "  Chế độ grok tạo video  ")
        self.tabWidget.addTab(self.tab_veo3,     "  Chế độ Veo3 tạo video  ")
        self.tabWidget.addTab(self.tab_seedance, "  Chế độ Seedance 2.0 video  ")
        self.tabWidget.addTab(self.tab_kol,      "  🌟 KOL AI  ")
        self.tabWidget.setCurrentIndex(1)

        rv.addWidget(self.tabWidget)

        root.addWidget(self.leftPanel)
        root.addWidget(self.rightPanel, 1)

        self._apply_qss()
        self.retranslateUi(Widget)
        QtCore.QMetaObject.connectSlotsByName(Widget)

    # ─── BUILD EACH TAB ───
    def _build_tab_content(self, tab, prefix):
        sc = self._sc
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(_s(14,sc), _s(10,sc), _s(14,sc), _s(10,sc))
        layout.setSpacing(_s(8,sc))

        # Top row: language + version + New
        topRow = QtWidgets.QHBoxLayout()
        lang_cb = self._combo(["Tiếng Việt (Vietnamese)", "English", "Japanese"])
        lang_cb.setMinimumWidth(_s(180, sc))
        ver_lb = QtWidgets.QLabel("v1.5.9")
        ver_lb.setObjectName("verLabel")
        new_btn = QtWidgets.QPushButton("● New")
        new_btn.setObjectName("newBtn")
        new_btn.setFixedHeight(_s(36, sc))
        topRow.addWidget(lang_cb)
        topRow.addWidget(ver_lb)
        topRow.addStretch()
        topRow.addWidget(new_btn)
        layout.addLayout(topRow)
        setattr(self, f"{prefix}_cb_lang", lang_cb)
        setattr(self, f"{prefix}_btn_new", new_btn)

        # Link input
        le_link = QtWidgets.QLineEdit()
        le_link.setPlaceholderText("https://www.youtube.com/shorts/bQic0POmBHA")
        le_link.setObjectName("bigInput")
        le_link.setFixedHeight(_s(38, sc))
        layout.addWidget(le_link)
        setattr(self, f"{prefix}_le_link", le_link)

        # Desc input
        le_desc = QtWidgets.QLineEdit()
        le_desc.setPlaceholderText("Mô tả thêm (tùy chọn)...")
        le_desc.setObjectName("bigInput")
        le_desc.setFixedHeight(_s(38, sc))
        layout.addWidget(le_desc)
        setattr(self, f"{prefix}_le_desc", le_desc)

        # Analyze button
        btn_analyze = QtWidgets.QPushButton("🚀  BẮT ĐẦU TẠO VIDEO")
        btn_analyze.setObjectName("analyzeBtn")
        btn_analyze.setFixedHeight(_s(48, sc))
        layout.addWidget(btn_analyze)
        setattr(self, f"{prefix}_btn_analyze", btn_analyze)

        # Action buttons row
        actionRow = QtWidgets.QHBoxLayout()
        actionRow.setSpacing(_s(5, sc))
        actions = [
            ("⏱ Đang xử lý...  0/10",     "actionBtnProcess", f"{prefix}_btn_running"),
            ("🎬 Ghép Video",               "actionBtnMerge",   f"{prefix}_btn_merge"),
            ("🔁 Chạy lại cảnh nhất định",  "actionBtnRerun",   f"{prefix}_btn_rerun"),
            ("✏️ Thêm kịch bản",            "actionBtnAdd",     f"{prefix}_btn_add"),
            ("⚙️ Khác",                     "actionBtnMore",    f"{prefix}_btn_more"),
        ]
        for text, obj, attr in actions:
            b = QtWidgets.QPushButton(text)
            b.setObjectName(obj)
            b.setFixedHeight(_s(36, sc))
            b.setCursor(QtCore.Qt.PointingHandCursor)
            actionRow.addWidget(b)
            setattr(self, attr, b)
        actionRow.addStretch()
        layout.addLayout(actionRow)

        # Reference image box
        refBox = QtWidgets.QFrame()
        refBox.setObjectName("refBox")
        refBox.setFixedHeight(_s(78, sc))
        refLayout = QtWidgets.QHBoxLayout(refBox)
        refLayout.setContentsMargins(_s(10,sc), _s(6,sc), _s(10,sc), _s(6,sc))
        refLayout.setSpacing(_s(12,sc))

        ref_img_lb = QtWidgets.QLabel("ẢNH THAM CHIẾU")
        ref_img_lb.setObjectName("refImgBox")
        ref_img_lb.setAlignment(QtCore.Qt.AlignCenter)
        ref_img_lb.setFixedWidth(_s(160, sc))

        ref_txt = QtWidgets.QLabel(
            "MEO ME (Adult female cat, white fur, red dress...)  "
            "MEO BO (Adult male cat, orange tabby fur, strong posture...)"
        )
        ref_txt.setObjectName("orangeText")
        ref_txt.setWordWrap(True)

        refLayout.addWidget(ref_img_lb)
        refLayout.addWidget(ref_txt, 1)
        layout.addWidget(refBox)
        setattr(self, f"{prefix}_ref_img", ref_img_lb)
        setattr(self, f"{prefix}_ref_txt", ref_txt)

        # Scene scroll
        scene_scroll = QtWidgets.QScrollArea()
        scene_scroll.setWidgetResizable(True)
        scene_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scene_box = QtWidgets.QWidget()
        scene_box.setObjectName("sceneBox")
        scene_layout = QtWidgets.QVBoxLayout(scene_box)
        scene_layout.setContentsMargins(0, 0, 0, 0)
        scene_layout.setSpacing(_s(8, sc))

        for i in range(1, 11):
            card = self._scene_card(i, active=(i == 1))
            scene_layout.addWidget(card)

        scene_layout.addStretch()
        scene_scroll.setWidget(scene_box)
        layout.addWidget(scene_scroll, 1)

    # ─── SCENE CARD ───
    def _scene_card(self, idx, active=False):
        sc = self._sc
        card = QtWidgets.QFrame()
        card.setObjectName("sceneCardActive" if active else "sceneCard")
        card.setMinimumHeight(_s(160, sc))
        card.setMaximumHeight(_s(180, sc))

        hl = QtWidgets.QHBoxLayout(card)
        hl.setContentsMargins(_s(10,sc), _s(10,sc), _s(10,sc), _s(10,sc))
        hl.setSpacing(_s(12,sc))

        preview = QtWidgets.QLabel(f"SCENE {idx}")
        preview.setObjectName("previewBox")
        preview.setAlignment(QtCore.Qt.AlignCenter)
        preview.setFixedSize(_s(180, sc), _s(100, sc))

        vr = QtWidgets.QVBoxLayout()
        vr.setSpacing(_s(4, sc))

        title = QtWidgets.QLabel(f"☑  CẢNH {idx}")
        title.setObjectName("sceneTitle")

        prompt_lb = QtWidgets.QLabel("VIDEO PROMPT")
        prompt_lb.setObjectName("blueLabel")

        prompt = QtWidgets.QTextEdit()
        prompt.setObjectName("promptBox")
        prompt.setFixedHeight(_s(54, sc))
        prompt.setPlainText(
            "anime style, vibrant colors, clean outlines, soft cel shading, "
            "detailed eyes, studio-quality anime frame, high-clarity character design..."
        )

        audio_lb = QtWidgets.QLabel("AUDIO / TTS")
        audio_lb.setObjectName("blueLabel")

        vr.addWidget(title)
        vr.addWidget(prompt_lb)
        vr.addWidget(prompt)
        vr.addWidget(audio_lb)

        hl.addWidget(preview)
        hl.addLayout(vr, 1)
        return card

    # ─── KOL TAB ───
    def _build_kol_tab(self, tab):
        sc = self._sc
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(_s(14,sc), _s(10,sc), _s(14,sc), _s(10,sc))
        layout.setSpacing(_s(8,sc))

        # ── Top row: language + version + New (giống Veo3)
        topRow = QtWidgets.QHBoxLayout()
        kol_lang_cb = self._combo(["Tiếng Việt (Vietnamese)", "English", "Japanese"])
        kol_lang_cb.setMinimumWidth(_s(220, sc))
        kol_ver_lb = QtWidgets.QLabel("v1.5.9")
        kol_ver_lb.setObjectName("verLabel")
        kol_new_btn = QtWidgets.QPushButton("● New")
        kol_new_btn.setObjectName("newBtn")
        kol_new_btn.setFixedHeight(_s(36, sc))
        topRow.addWidget(kol_lang_cb)
        topRow.addWidget(kol_ver_lb)
        topRow.addStretch()
        topRow.addWidget(kol_new_btn)
        layout.addLayout(topRow)
        self.kol_cb_lang = kol_lang_cb
        self.kol_btn_new = kol_new_btn

        # ── Link input (giống Veo3)
        kol_le_link = QtWidgets.QLineEdit()
        kol_le_link.setPlaceholderText("https://www.youtube.com/shorts/bQic0POmBHA")
        kol_le_link.setObjectName("bigInput")
        kol_le_link.setFixedHeight(_s(38, sc))
        layout.addWidget(kol_le_link)
        self.kol_le_link = kol_le_link

        # ── Desc input (giống Veo3)
        kol_le_desc = QtWidgets.QLineEdit()
        kol_le_desc.setPlaceholderText("Mô tả thêm (tùy chọn)...")
        kol_le_desc.setObjectName("bigInput")
        kol_le_desc.setFixedHeight(_s(38, sc))
        layout.addWidget(kol_le_desc)
        self.kol_le_desc = kol_le_desc

        # ── Analyze button (giống Veo3)
        kol_btn_analyze = QtWidgets.QPushButton("🚀  BẮT ĐẦU TẠO VIDEO")
        kol_btn_analyze.setObjectName("kolAnalyzeBtn")
        kol_btn_analyze.setFixedHeight(_s(48, sc))
        layout.addWidget(kol_btn_analyze)
        self.kol_btn_analyze = kol_btn_analyze

        # ── Action buttons row (giống Veo3)
        actionRow = QtWidgets.QHBoxLayout()
        actionRow.setSpacing(_s(3, sc))
        kol_actions = [
            ("⏱ Đang xử lý...  0/10",    "actionBtnProcess", "kol_btn_running"),
            ("🎬 Ghép Video",              "actionBtnMerge",   "kol_btn_merge"),
            ("🔁 Chạy lại cảnh nhất định", "actionBtnRerun",   "kol_btn_rerun"),
            ("✏️ Thêm kịch bản",           "actionBtnAdd",     "kol_btn_add"),
            ("⚙️ Khác",                    "actionBtnMore",    "kol_btn_more"),
        ]
        for text, obj, attr in kol_actions:
            b = QtWidgets.QPushButton(text)
            b.setObjectName(obj)
            b.setFixedHeight(_s(36, sc))
            b.setCursor(QtCore.Qt.PointingHandCursor)
            actionRow.addWidget(b)
            setattr(self, attr, b)
        actionRow.addStretch()
        layout.addLayout(actionRow)

        # ══════════════════════════════════════════════
        # ── KOL SELECTOR PANEL (phần đặc trưng của tab này)
        # ══════════════════════════════════════════════
        kolPanel = QtWidgets.QFrame()
        kolPanel.setObjectName("kolPanel")
        kolPanelLay = QtWidgets.QVBoxLayout(kolPanel)
        kolPanelLay.setContentsMargins(_s(10,sc), _s(8,sc), _s(10,sc), _s(8,sc))
        kolPanelLay.setSpacing(_s(6,sc))

        # Label tiêu đề panel
        kolTitleRow = QtWidgets.QHBoxLayout()
        kolTitle = QtWidgets.QLabel("🌟  CHỌN KOL MẪU")
        kolTitle.setObjectName("kolPanelTitle")
        kolTitleRow.addWidget(kolTitle)
        kolTitleRow.addStretch()
        kolPanelLay.addLayout(kolTitleRow)

        # 6 KOL avatar ngang
        kolRow = QtWidgets.QHBoxLayout()
        kolRow.setSpacing(_s(8, sc))
        kol_presets = [
            ("👩", "Linh Beauty",   "#ec4899"),
            ("👨", "Nam Tech",      "#3b82f6"),
            ("👩", "Mai Ẩm Thực",  "#f59e0b"),
            ("🧑", "Khoa Travel",  "#10b981"),
            ("👩", "Hà Lifestyle", "#8b5cf6"),
            ("👨", "Tuấn Fitness", "#ef4444"),
        ]
        self.kol_preset_btns = []
        for emo, name, color in kol_presets:
            kolBtn = self._kol_mini_btn(emo, name, color)
            kolRow.addWidget(kolBtn)
            self.kol_preset_btns.append(kolBtn)
        kolRow.addStretch()
        kolPanelLay.addLayout(kolRow)

        # Dòng nhập prompt KOL + upload ảnh
        promptRow = QtWidgets.QHBoxLayout()
        promptRow.setSpacing(_s(8, sc))

        kol_prompt = QtWidgets.QLineEdit()
        kol_prompt.setPlaceholderText("✍️  Nhập mô tả KOL (phong cách, giọng nói, ngoại hình...)...")
        kol_prompt.setObjectName("kolPromptInput")
        kol_prompt.setFixedHeight(_s(36, sc))
        self.kol_le_prompt = kol_prompt

        kol_upload_btn = QtWidgets.QPushButton("📷  Gửi ảnh KOL")
        kol_upload_btn.setObjectName("kolUploadBtn")
        kol_upload_btn.setFixedHeight(_s(36, sc))
        kol_upload_btn.setFixedWidth(_s(120, sc))
        kol_upload_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.kol_btn_upload = kol_upload_btn

        promptRow.addWidget(kol_prompt, 1)
        promptRow.addWidget(kol_upload_btn)
        kolPanelLay.addLayout(promptRow)

        layout.addWidget(kolPanel)

        # ── Reference image box (giống Veo3)
        refBox = QtWidgets.QFrame()
        refBox.setObjectName("refBox")
        refBox.setFixedHeight(_s(78, sc))
        refLayout = QtWidgets.QHBoxLayout(refBox)
        refLayout.setContentsMargins(_s(10,sc), _s(6,sc), _s(10,sc), _s(6,sc))
        refLayout.setSpacing(_s(12,sc))
        ref_img_lb = QtWidgets.QLabel("ẢNH THAM CHIẾU")
        ref_img_lb.setObjectName("refImgBox")
        ref_img_lb.setAlignment(QtCore.Qt.AlignCenter)
        ref_img_lb.setFixedWidth(_s(160, sc))
        ref_txt = QtWidgets.QLabel(
            "KOL (Phong cách, ngoại hình, giọng nói...)  "
            "VIDEO (Nội dung, cảnh quay, hiệu ứng...)"
        )
        ref_txt.setObjectName("orangeText")
        ref_txt.setWordWrap(True)
        refLayout.addWidget(ref_img_lb)
        refLayout.addWidget(ref_txt, 1)
        layout.addWidget(refBox)
        self.kol_ref_img = ref_img_lb
        self.kol_ref_txt = ref_txt

        # ── Scene scroll (giống Veo3)
        scene_scroll = QtWidgets.QScrollArea()
        scene_scroll.setWidgetResizable(True)
        scene_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scene_box = QtWidgets.QWidget()
        scene_box.setObjectName("sceneBox")
        scene_layout = QtWidgets.QVBoxLayout(scene_box)
        scene_layout.setContentsMargins(0, 0, 0, 0)
        scene_layout.setSpacing(_s(8, sc))
        for i in range(1, 11):
            card = self._scene_card(i, active=(i == 1))
            scene_layout.addWidget(card)
        scene_layout.addStretch()
        scene_scroll.setWidget(scene_box)
        layout.addWidget(scene_scroll, 1)

    def _kol_mini_btn(self, emoji, name, accent):
        sc = self._sc
        frame = QtWidgets.QFrame()
        frame.setObjectName("kolMiniCard")
        frame.setCursor(QtCore.Qt.PointingHandCursor)
        frame.setFixedWidth(_s(96, sc))
        frame.setFixedHeight(_s(76, sc))
        frame.setStyleSheet(
            f"#kolMiniCard {{ background: #0f172a; border: 1px solid {accent}55;"
            f" border-radius: {_s(8,sc)}px; }}"
            f"#kolMiniCard:hover {{ border: 2px solid {accent}; background: {accent}18; }}"
        )
        vl = QtWidgets.QVBoxLayout(frame)
        vl.setContentsMargins(_s(4,sc), _s(6,sc), _s(4,sc), _s(4,sc))
        vl.setSpacing(_s(2,sc))

        emo_lb = QtWidgets.QLabel(emoji)
        emo_lb.setAlignment(QtCore.Qt.AlignCenter)
        emo_lb.setStyleSheet(
            f"font-size: {_s(22,sc)}px; background: transparent; border: none;"
            f" border-radius: {_s(16,sc)}px;"
        )

        name_lb = QtWidgets.QLabel(name)
        name_lb.setAlignment(QtCore.Qt.AlignCenter)
        name_lb.setWordWrap(True)
        name_lb.setStyleSheet(
            f"color: #e2e8f0; font-size: {_s(9,sc)}px; font-weight: bold;"
            f" background: transparent; border: none;"
        )

        vl.addWidget(emo_lb)
        vl.addWidget(name_lb)
        return frame

    # ─── HELPERS ───
    def _lbl_save_row(self, widget, attr):
        sc = self._sc
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(_s(6, sc))
        btn = QtWidgets.QPushButton("Lưu")
        btn.setObjectName("saveBtn")
        btn.setFixedSize(_s(56, sc), _s(34, sc))
        row.addWidget(widget, 1)
        row.addWidget(btn)
        setattr(self, attr, btn)
        return row

    def _combo(self, items):
        cb = QtWidgets.QComboBox()
        cb.addItems(items)
        cb.setFixedHeight(_s(28, self._sc))
        return cb

    def _le(self, placeholder="", password=False):
        le = QtWidgets.QLineEdit()
        le.setPlaceholderText(placeholder)
        le.setFixedHeight(_s(28, self._sc))
        if password:
            le.setEchoMode(QtWidgets.QLineEdit.Password)
        return le

    def _lbl(self, text, obj=""):
        lb = QtWidgets.QLabel(text)
        if obj:
            lb.setObjectName(obj)
        return lb

    def _hline(self):
        f = QtWidgets.QFrame()
        f.setFrameShape(QtWidgets.QFrame.HLine)
        f.setObjectName("hline")
        return f

    def _toggle_row(self, text, checked=False):
        sc = self._sc
        row = QtWidgets.QFrame()
        row.setObjectName("switchRow")
        row.setFixedHeight(_s(34, sc))
        hl = QtWidgets.QHBoxLayout(row)
        hl.setContentsMargins(_s(8,sc), 2, _s(8,sc), 2)
        lb = QtWidgets.QLabel(text)
        lb.setObjectName("switchLabel")
        cb = QtWidgets.QCheckBox()
        cb.setChecked(checked)
        hl.addWidget(lb)
        hl.addStretch()
        hl.addWidget(cb)
        return row

    def _toggle_left(self, text, checked=False):
        cb = QtWidgets.QCheckBox(text)
        cb.setChecked(checked)
        cb.setObjectName("toggleLeft")
        cb.setCursor(QtCore.Qt.PointingHandCursor)
        return cb

    # ─── QSS ───
    def _apply_qss(self):
        sc = self._sc
        fs    = _s(13, sc)
        fs_sm = _s(12, sc)
        fs_lg = _s(16, sc)
        fs_tab= _s(14, sc)
        r     = _s(6, sc)
        tp    = _s(8, sc)
        th    = _s(8, sc)

        qss = f"""
        QWidget {{
            background-color: #07111f;
            color: #e5e7eb;
            font-family: 'Segoe UI', Arial;
            font-size: {fs}px;
        }}
        #leftPanel {{
            background-color: #07111f;
            border-right: 1px solid #1e293b;
        }}
        #leftBox {{ background-color: transparent; }}
        #rightPanel {{ background-color: #0a1628; }}

        /* ── TABS ── */
        QTabWidget::pane {{ background-color: #0a1628; border: none; }}
        QTabBar::tab {{
            background: #050e1a;
            color: #6b7280;
            padding: {th}px {tp}px;
            font-size: {fs_tab}px;
            font-weight: bold;
            border: none;
            border-bottom: 3px solid transparent;
        }}
        QTabBar::tab:selected {{
            background: #7c3aed;
            color: #ffffff;
            border-bottom: 3px solid #a855f7;
        }}
        QTabBar::tab:hover {{ background: #111827; color: #e5e7eb; }}

        /* ── LABELS ── */
        #sectionTitle {{
            color: #ffffff;
            font-size: {fs_lg}px;
            font-weight: bold;
            margin-top: {_s(4,sc)}px;
        }}
        #grpLabel {{ color: #94a3b8; font-size: {fs_sm}px; font-weight: bold; }}
        #noteLabel {{ color: #64748b; font-size: {_s(10,sc)}px; font-style: italic; }}
        #warnLabel {{ color: #f59e0b; font-size: {_s(10,sc)}px; font-weight: bold; }}
        #smallBlue {{ color: #60a5fa; font-size: {fs_sm}px; }}
        #verLabel  {{ color: #94a3b8; font-size: {fs_sm}px; }}
        #sceneTitle {{ color: #bfdbfe; font-weight: bold; font-size: {fs_sm}px; }}
        #blueLabel  {{ color: #38bdf8; font-size: {fs_sm}px; font-weight: bold; }}
        #orangeText {{ color: #f59e0b; font-weight: bold; font-size: {fs_sm}px; }}

        /* ── INPUTS ── */
        QLineEdit, QTextEdit, QComboBox, QSpinBox {{
            background-color: #111827;
            color: #e5e7eb;
            border: 1px solid #1e3a5f;
            border-radius: {r}px;
            padding: {_s(4,sc)}px {_s(8,sc)}px;
            font-size: {fs}px;
        }}
        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {{ border: 1px solid #38bdf8; }}
        QSpinBox::up-button, QSpinBox::down-button {{ width: {_s(20,sc)}px; background: transparent; border: none; }}
        #bigInput {{ min-height: {_s(38,sc)}px; }}
        #promptBox {{ background: transparent; border: none; font-size: {fs_sm}px; color: #cbd5e1; font-style: italic; }}

        /* ── BUTTONS ── */
        QPushButton {{
            background-color: #1e293b;
            color: white;
            border: 1px solid #334155;
            border-radius: {r}px;
            padding: {_s(5,sc)}px {_s(10,sc)}px;
            font-size: {fs}px;
            font-weight: bold;
        }}
        QPushButton:hover   {{ background-color: #334155; }}
        QPushButton:pressed {{ background-color: #0f172a; }}

        #saveBtn {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #4ade80, stop:1 #16a34a);
            border: none; color: white; font-size: {fs_sm}px;
        }}
        #saveBtn:hover {{ background: #15803d; }}

        #durationInline {{
            color: #38bdf8;
            font-size: {fs_sm}px;
            font-weight: bold;
            padding: {_s(2,sc)}px 0;
        }}

        #openFolderBtn {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2684ff, stop:1 #1d4ed8);
            border: none; color: white; font-size: {fs}px;
        }}

        #proxyBrowseBtn {{
            background: #1e293b;
            border: 1px solid #334155;
            color: #94a3b8; font-size: {_s(14,sc)}px;
            border-radius: {_s(4,sc)}px;
        }}
        #proxyBrowseBtn:hover {{ background: #334155; color: white; }}

        #analyzeBtn {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7c3aed, stop:1 #c084fc);
            border: none; color: white; font-size: {_s(17,sc)}px;
        }}
        #analyzeBtn:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #6d28d9, stop:1 #a855f7); }}

        #newBtn {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7c3aed, stop:1 #c084fc);
            border: none; color: white; font-size: {fs_sm}px;
        }}

        /* ── ACTION BUTTONS ── */
        #actionBtnProcess {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #1d4ed8, stop:1 #3b82f6);
            border: 1px solid #2563eb;
            color: white; font-size: {_s(11,sc)}px;
            padding: {_s(3,sc)}px {_s(10,sc)}px;
            border-radius: {_s(6,sc)}px;
            font-weight: bold;
        }}
        #actionBtnProcess:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #1e40af, stop:1 #2563eb); }}

        #actionBtnMerge {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7c3aed, stop:1 #a855f7);
            border: 1px solid #8b5cf6;
            color: white; font-size: {_s(11,sc)}px;
            padding: {_s(3,sc)}px {_s(10,sc)}px;
            border-radius: {_s(6,sc)}px;
            font-weight: bold;
        }}
        #actionBtnMerge:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #6d28d9, stop:1 #9333ea); }}

        #actionBtnRerun {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #0e7490, stop:1 #06b6d4);
            border: 1px solid #0891b2;
            color: white; font-size: {_s(11,sc)}px;
            padding: {_s(3,sc)}px {_s(10,sc)}px;
            border-radius: {_s(6,sc)}px;
            font-weight: bold;
        }}
        #actionBtnRerun:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #0c5f73, stop:1 #0891b2); }}

        #actionBtnAdd {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #166534, stop:1 #22c55e);
            border: 1px solid #16a34a;
            color: white; font-size: {_s(11,sc)}px;
            padding: {_s(3,sc)}px {_s(10,sc)}px;
            border-radius: {_s(6,sc)}px;
            font-weight: bold;
        }}
        #actionBtnAdd:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #14532d, stop:1 #16a34a); }}

        #actionBtnMore {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #78350f, stop:1 #f59e0b);
            border: 1px solid #d97706;
            color: white; font-size: {_s(11,sc)}px;
            padding: {_s(3,sc)}px {_s(10,sc)}px;
            border-radius: {_s(6,sc)}px;
            font-weight: bold;
        }}
        #actionBtnMore:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #713f12, stop:1 #d97706); }}

        /* ── CARDS ── */
        #refBox {{
            background: rgba(15,23,42,180);
            border: 1px solid #16a34a;
            border-radius: {_s(10,sc)}px;
        }}
        #refImgBox {{
            background: #020617; color: #64748b;
            border: 1px solid #334155; border-radius: {_s(6,sc)}px;
            font-weight: bold; font-size: {fs_sm}px;
        }}
        #sceneCard {{
            background: rgba(15,23,42,210);
            border: 1px dashed #f59e0b;
            border-radius: {_s(10,sc)}px;
        }}
        #sceneCardActive {{
            background: rgba(15,23,42,230);
            border: 1px solid #22c55e;
            border-radius: {_s(10,sc)}px;
        }}
        #previewBox {{
            background: #020617; color: #94a3b8;
            border: 1px solid #334155; border-radius: {_s(6,sc)}px;
            font-weight: bold; font-size: {fs_sm}px;
        }}
        #sceneBox {{ background: transparent; }}

        /* ── SWITCH ROW ── */
        #switchRow {{
            background-color: #111827;
            border: 1px solid #1f2937;
            border-radius: {r}px;
        }}
        #switchLabel {{ color: #e5e7eb; font-size: {fs_sm}px; }}

        #warnBox {{
            background-color: #0f172a;
            border: 1px solid #1e293b;
            border-radius: {r}px;
        }}
        #warnIcon {{ color: #f59e0b; font-size: {_s(16,sc)}px; }}
        #warnBoxText {{ color: #f59e0b; font-size: {fs_sm}px; font-weight: bold; }}

        #toggleLeft {{
            color: #e5e7eb;
            font-size: {fs}px;
            spacing: {_s(8,sc)}px;
        }}
        #toggleLeft::indicator {{
            width: {_s(32,sc)}px;
            height: {_s(18,sc)}px;
            border-radius: {_s(9,sc)}px;
            background-color: #1e293b;
            border: 1px solid #334155;
        }}
        #toggleLeft::indicator:checked {{
            background-color: #8b5cf6;
            border: 1px solid #7c3aed;
        }}

        /* ── KOL TAB ── */
        #kolAnalyzeBtn {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #be185d, stop:1 #ec4899);
            border: none; color: white; font-size: {_s(15,sc)}px; font-weight: bold;
        }}
        #kolAnalyzeBtn:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #9d174d, stop:1 #db2777); }}

        #kolPanel {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #130520, stop:1 #0f172a);
            border: 1px solid #4c1d95;
            border-radius: {_s(8,sc)}px;
        }}
        #kolPanelTitle {{
            color: #e9d5ff; font-size: {fs}px; font-weight: bold;
        }}
        #kolPromptInput {{
            background: #111827; border: 1px solid #4c1d95;
            border-radius: {_s(6,sc)}px; color: #e5e7eb;
            padding: 0 {_s(10,sc)}px; font-size: {fs}px;
        }}
        #kolPromptInput:focus {{ border: 1px solid #a855f7; }}
        #kolUploadBtn {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4c1d95, stop:1 #7c3aed);
            border: none; color: white; font-size: {fs_sm}px; font-weight: bold;
            border-radius: {_s(6,sc)}px;
        }}
        #kolUploadBtn:hover {{ background: #6d28d9; }}

        /* ── MISC ── */
        #hline {{ background: #1e293b; color: #1e293b; max-height: 1px; }}

        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{
            background: #0f172a; width: {_s(7,sc)}px; border-radius: {_s(3,sc)}px;
        }}
        QScrollBar::handle:vertical {{
            background: #334155; border-radius: {_s(3,sc)}px; min-height: {_s(18,sc)}px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

        QComboBox::drop-down {{ border: none; }}
        QComboBox QAbstractItemView {{
            background: #111827; color: #e5e7eb;
            selection-background-color: #1e40af; font-size: {fs}px;
        }}
        """
        self.centralwidget.parent().setStyleSheet(qss)

    def retranslateUi(self, Widget):
        Widget.setWindowTitle("🎬 AI Video Tool - Grok / Veo3 / Seedance 2.0")

# test 1
# if __name__ == "__main__":
#     import sys
#     from PyQt5.QtWidgets import QApplication, QMainWindow
#     app = QApplication(sys.argv)
#     w = QMainWindow()
#     ui = Ui_Widget()
#     ui.setupUi(w)
#     w.showMaximized()
#     sys.exit(app.exec_())
