import tkinter as tk
from tkinter import ttk
from system.config.loader import save_settings
from system.config.settings import ReplicaSettings


class SettingsPanel:
    def __init__(self, root, settings, on_saved=None):
        self.root = root
        self.settings = settings
        self.on_saved = on_saved

    def open(self):
        window = tk.Toplevel(self.root)
        window.title("Настройки Replica")
        window.geometry("500x950")
        window.configure(bg="#121212")

        # --- СТИЛИ ---
        style = ttk.Style()
        style.theme_use('clam')
        bg, fg, field_bg, accent = "#121212", "#ffffff", "#252525", "#0078D7"

        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TLabelframe", background="#1e1e1e", borderwidth=0)
        style.configure("TLabelframe.Label", background="#1e1e1e", foreground=accent, font=("Segoe UI", 10, "bold"))
        style.configure("TCheckbutton", background="#1e1e1e", foreground=fg)
        style.configure("TEntry", fieldbackground=field_bg, foreground=fg, borderwidth=0, padding=5)
        style.configure("TCombobox", fieldbackground=field_bg, foreground=fg, borderwidth=0)
        style.configure("TSpinbox", fieldbackground=field_bg, foreground=fg, borderwidth=0)
        style.configure("Modern.TButton", background=accent, foreground="white", borderwidth=0, padding=10)

        container = ttk.Frame(window, padding=20)
        container.pack(fill="both", expand=True)

        # --- ПЕРЕМЕННЫЕ ---
        lang_var = tk.StringVar(value=self.settings.language)
        auto_var = tk.BooleanVar(value=self.settings.autostart)
        auto_hide_var = tk.BooleanVar(value=self.settings.interface.auto_hide)
        size_var = tk.IntVar(value=self.settings.interface.avatar_size)
        vol_var = tk.DoubleVar(value=self.settings.volume)

        llm_var = tk.StringVar(value=self.settings.ai.llm_model)
        vision_var = tk.StringVar(value=self.settings.ai.vision_model)
        stt_var = tk.StringVar(value=self.settings.ai.speech_model)
        tts_m_var = tk.StringVar(value=self.settings.ai.tts_model)
        perf_var = tk.StringVar(value=self.settings.ai.performance_mode)
        gpu_var = tk.BooleanVar(value=self.settings.ai.use_gpu)
        mem_var = tk.IntVar(value=self.settings.ai.memory_limit_mb)

        wake_var = tk.BooleanVar(value=self.settings.voice.wake_word_enabled)
        cont_var = tk.BooleanVar(value=self.settings.voice.continuous_listening)
        mic_var = tk.StringVar(value=self.settings.voice.microphone_name)

        screen_en_var = tk.BooleanVar(value=self.settings.screen.enabled)
        int_var = tk.IntVar(value=self.settings.screen.interval_seconds)

        # --- СЕКЦИИ ---
        def create_frame(text):
            f = ttk.LabelFrame(container, text=f" {text} ", padding=10)
            f.pack(fill="x", pady=5)
            return f

        f_gen = create_frame("ГЛОБАЛЬНЫЕ")
        f_ai = create_frame("AI & МОДЕЛИ")
        f_voice = create_frame("ГОЛОС & МИКРОФОН")
        f_screen = create_frame("АНАЛИЗ ЭКРАНА")
        f_ui = create_frame("ИНТЕРФЕЙС")

        # Глобал
        ttk.Label(f_gen, text="Язык:").pack(anchor="w");
        ttk.Entry(f_gen, textvariable=lang_var).pack(fill="x")
        ttk.Checkbutton(f_gen, text="Автозапуск", variable=auto_var).pack(anchor="w")
        ttk.Label(f_gen, text="Громкость:").pack(anchor="w");
        ttk.Scale(f_gen, from_=0, to=1, variable=vol_var, orient="horizontal").pack(fill="x")

        # AI
        ttk.Label(f_ai, text="LLM Модель:").pack(anchor="w");
        ttk.Entry(f_ai, textvariable=llm_var).pack(fill="x")
        ttk.Label(f_ai, text="Vision Модель:").pack(anchor="w");
        ttk.Entry(f_ai, textvariable=vision_var).pack(fill="x")
        ttk.Label(f_ai, text="Лимит памяти (MB):").pack(anchor="w");
        ttk.Spinbox(f_ai, from_=512, to=8192, textvariable=mem_var).pack(fill="x")
        ttk.Checkbutton(f_ai, text="Использовать GPU", variable=gpu_var).pack(anchor="w")

        # Voice
        ttk.Checkbutton(f_voice, text="Wake word", variable=wake_var).pack(anchor="w")
        ttk.Checkbutton(f_voice, text="Постоянное прослушивание", variable=cont_var).pack(anchor="w")
        ttk.Label(f_voice, text="Микрофон:").pack(anchor="w");
        ttk.Entry(f_voice, textvariable=mic_var).pack(fill="x")

        # Screen
        ttk.Checkbutton(f_screen, text="Анализ включен", variable=screen_en_var).pack(anchor="w")
        ttk.Label(f_screen, text="Интервал (сек):").pack(anchor="w");
        ttk.Spinbox(f_screen, from_=1, to=300, textvariable=int_var).pack(fill="x")

        # UI (Размер аватара + Авто-скрытие)
        ttk.Label(f_ui, text="Размер аватара:").pack(anchor="w")
        ttk.Spinbox(f_ui, from_=64, to=256, textvariable=size_var).pack(fill="x")
        ttk.Checkbutton(f_ui, text="Авто-скрытие текста", variable=auto_hide_var).pack(anchor="w", pady=5)

        # --- СОХРАНЕНИЕ ---
        def save():
            self.settings.language = lang_var.get()
            self.settings.autostart = auto_var.get()
            self.settings.volume = vol_var.get()
            self.settings.ai.llm_model = llm_var.get()
            self.settings.ai.vision_model = vision_var.get()
            self.settings.ai.speech_model = stt_var.get()
            self.settings.ai.tts_model = tts_m_var.get()
            self.settings.ai.performance_mode = perf_var.get()
            self.settings.ai.use_gpu = gpu_var.get()
            self.settings.ai.memory_limit_mb = mem_var.get()
            self.settings.voice.wake_word_enabled = wake_var.get()
            self.settings.voice.continuous_listening = cont_var.get()
            self.settings.voice.microphone_name = mic_var.get()
            self.settings.screen.enabled = screen_en_var.get()
            self.settings.screen.interval_seconds = int(int_var.get())
            self.settings.interface.auto_hide = auto_hide_var.get()
            self.settings.interface.avatar_size = int(size_var.get())

            save_settings(self.settings)
            if self.on_saved: self.on_saved()
            window.destroy()

        ttk.Button(container, text="СОХРАНИТЬ", command=save, style="Modern.TButton").pack(fill="x", pady=20, ipady=5)