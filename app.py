import streamlit as st
import speech_recognition as sr
import re
import io
import os

from rapidfuzz import fuzz
from streamlit_mic_recorder import mic_recorder

# ==========================================
# НАСТРОЙКИ
# ==========================================

st.set_page_config(
    page_title="ReadMotion — Три поросёнка",
    page_icon="🐷",
    layout="centered"
)


# ==========================================
# ДИЗАЙН
# ==========================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
}

.stApp {
    background: #FFF8F1;
}

.block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

h1, h2, h3 {
    color: #513D48 !important;
    font-weight: 900 !important;
}

p, label {
    color: #6E5A62;
}

.hero {
    background: linear-gradient(135deg, #FFE2E7, #FFEEDC);
    border-radius: 28px;
    padding: 30px;
    text-align: center;
    margin-bottom: 25px;
    border: 2px solid #FFFFFF;
}

.hero-title {
    font-size: 42px;
    font-weight: 900;
    color: #513D48;
    margin: 0;
}

.hero-subtitle {
    color: #866B77;
    font-size: 17px;
    margin-top: 8px;
}

.pig {
    font-size: 65px;
    margin-bottom: 5px;
}

.story-card {
    background: #FFFFFF;
    border-radius: 24px;
    padding: 28px;
    border: 2px solid #F4E5DB;
    box-shadow: 0 5px 18px rgba(100, 70, 70, 0.05);
    margin-top: 15px;
    margin-bottom: 20px;
}

.story-text {
    font-size: 22px;
    line-height: 1.9;
    color: #57434A;
    font-weight: 600;
}

.episode-label {
    background: #FCE4EA;
    color: #B45F78;
    border-radius: 30px;
    padding: 7px 16px;
    display: inline-block;
    font-weight: 800;
    font-size: 14px;
}

.reward-card {
    background: linear-gradient(135deg, #FFF0C9, #FFE5C9);
    border-radius: 24px;
    padding: 25px;
    text-align: center;
    border: 2px solid #FFFFFF;
    margin-top: 20px;
}

.reward-title {
    color: #75502F;
    font-size: 25px;
    font-weight: 900;
}

.reward-stars {
    font-size: 35px;
    letter-spacing: 7px;
}

.info-card {
    background: #F1EAFE;
    padding: 18px;
    border-radius: 18px;
    color: #65517D;
    margin: 15px 0;
}

div.stButton > button {
    border-radius: 16px;
    border: none;
    background: #F3A8B8;
    color: #593C48;
    font-weight: 900;
    min-height: 48px;
    transition: 0.2s;
}

div.stButton > button:hover {
    background: #ED8FA6;
    color: white;
    border: none;
}

div.stButton > button[kind="primary"] {
    background: #83C9A5;
    color: #294D3B;
}

div.stButton > button[kind="primary"]:hover {
    background: #64B88D;
    color: white;
}

[data-testid="stProgressBar"] > div > div {
    background: #F0A0B5;
}

footer {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# СКАЗКА
# ==========================================

episodes = [
    {
        "title": "Три поросёнка",
        "emoji": "🐷",
        "text": (
            "Давным-давно жили-были три поросёнка. "
            "Их звали Пип, Пуп и Пап. "
            "Однажды поросята решили построить себе отдельные дома."
            "Они вышли из маминого дома и отправились в сторону леса."
        )
    },
    {
        "title": "Соломенный дом",
        "emoji": "🌾",
        "text": (
            "Первый поросёнок, Пип, захотел построить дом как можно быстрее. "
            "Он собрал вокруг солому и начал возводить маленький домик. "
            "За короткое время его дом был готов. "
            "Пип зашёл внутрь и лёг отдыхать. "
        )
    },
    {
        "title": "Деревянный дом",
        "emoji": "🪵",
        "text": (
            "Второй поросёнок, Пуп, не захотел строить дом из соломы. "
            "Он собрал деревянные доски и построил дом из дерева. "
            "Его дом получился крепче, чем дом первого поросёнка. "
            "Довольный своей работой, Пуп зашёл в дом. "
        )
    },
    {
        "title": "Кирпичный дом",
        "emoji": "🧱",
        "text": (
            "Третий поросёнок, Пап, был очень трудолюбивым. "
            "Он решил построить крепкий дом из кирпича. "
            "Хотя строительство требовало много времени, "
            "Пап работал не спеша. "
            "В конце концов его прочный дом был готов. "
        )
    },
    {
        "title": "Пришёл волк",
        "emoji": "🐺",
        "text": (
            "Однажды в лесу появился голодный волк. "
            "Он увидел соломенный домик первого поросёнка и постучал в дверь "
            "Поросёнок дверь не открыл. "
            "Тогда волк сильно дунул и разрушил соломенный дом. "
            "Испуганный Пип убежал в деревянный дом второго поросёнка. "
        )
    },
    {
        "title": "Счастливый финал",
        "emoji": "🏡",
        "text": (
            "Волк разрушил и деревянный дом второго поросёнка. "
            "Тогда оба поросёнка прибежали в кирпичный дом третьего брата. "
            "Волк попытался разрушить и этот дом, но сил у него не хватило. "
            "Тогда он решил забраться в дом через дымоход. "
            "Но поросята заранее вскипятили воду в котле. "
            "Волк испугался и убежал прочь. "
            "Три поросёнка остались в безопасном доме и с тех пор поняли цену труда. "
        )
    }
]


# ==========================================
# СОСТОЯНИЕ ПРИЛОЖЕНИЯ
# ==========================================

if "rm_episode" not in st.session_state:
    st.session_state.rm_episode = 0

if "rm_unlocked" not in st.session_state:
    st.session_state.rm_unlocked = False

if "rm_recognized" not in st.session_state:
    st.session_state.rm_recognized = ""

if "rm_score" not in st.session_state:
    st.session_state.rm_score = 0

if "rm_completed" not in st.session_state:
    st.session_state.rm_completed = []


# ==========================================
# ФУНКЦИИ
# ==========================================

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^а-яё\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def check_reading(original, spoken):
    return fuzz.ratio(
        normalize(original),
        normalize(spoken)
    )


def recognize_audio(audio_bytes):

    recognizer = sr.Recognizer()

    try:
        audio_file = sr.AudioFile(
            io.BytesIO(audio_bytes)
        )

        with audio_file as source:
            audio = recognizer.record(source)

        return recognizer.recognize_google(
            audio,
            language="ru-RU"
        )

    except sr.UnknownValueError:
        return None

    except sr.RequestError as error:
        st.error(f"Ошибка сервиса распознавания: {error}")
        return None

    except Exception as error:
        st.error(f"Ошибка обработки записи: {error}")
        return None


# ==========================================
# ШАПКА
# ==========================================

st.markdown("""
<div class="hero">
    <div class="pig">🐷 🐷 🐷</div>
    <div class="hero-title">ReadMotion</div>
    <div class="hero-subtitle">
        Читай сказки — оживляй истории!
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# БОКОВАЯ ИНФОРМАЦИЯ
# ==========================================

with st.sidebar:

    st.markdown("## 📚 ReadMotion")

    st.write("Наша первая сказка")

    st.markdown("### 🐷 Три поросёнка")

    st.progress(
        len(st.session_state.rm_completed) / len(episodes)
    )

    st.caption(
        f"Пройдено: {len(st.session_state.rm_completed)} "
        f"из {len(episodes)} эпизодов"
    )

    st.markdown("---")

    if st.button("🔄 Начать сказку заново"):

        st.session_state.rm_episode = 0
        st.session_state.rm_unlocked = False
        st.session_state.rm_recognized = ""
        st.session_state.rm_score = 0
        st.session_state.rm_completed = []

        st.rerun()

    st.markdown("---")
    st.caption("Создано с любовью ❤️")


# ==========================================
# ТЕКУЩИЙ ЭПИЗОД
# ==========================================

index = st.session_state.rm_episode

episode = episodes[index]

st.markdown(
    f'<div class="episode-label">'
    f'ЭПИЗОД {index + 1} ИЗ {len(episodes)}'
    f'</div>',
    unsafe_allow_html=True
)

st.progress((index + 1) / len(episodes))

st.markdown(
    f"## {episode['emoji']} {episode['title']}"
)

st.markdown(
    f"""
    <div class="story-card">
        <div class="story-text">
            {episode["text"]}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================
# ЧТЕНИЕ
# ==========================================

st.markdown("## 🎤 Время читать!")

st.markdown(
    '<div class="info-card">'
    'Прочитай сказку вслух. Не торопись, '
    'внимательно произноси слова. '
    'У тебя всё получится! ⭐'
    '</div>',
    unsafe_allow_html=True
)

audio = mic_recorder(
    start_prompt="🎤 Начать чтение",
    stop_prompt="⏹ Остановить чтение",
    key=f"rm_recorder_{index}",
    format="wav"
)


# ==========================================
# ПРОВЕРКА
# ==========================================

if audio and audio.get("bytes"):

    st.audio(
        audio["bytes"],
        format="audio/wav"
    )

    if st.button(
        "✨ Проверить моё чтение",
        key=f"rm_check_{index}",
        use_container_width=True
    ):

        with st.spinner("🐷 Слушаем твоё чтение..."):

            recognized = recognize_audio(
                audio["bytes"]
            )

        if recognized:

            score = check_reading(
                episode["text"],
                recognized
            )

            st.session_state.rm_recognized = recognized
            st.session_state.rm_score = score

            if score >= 55:
                st.session_state.rm_unlocked = True

            st.rerun()

        else:
            st.warning(
                "Не получилось разобрать запись. "
                "Попробуй ещё раз!"
            )


# ==========================================
# РЕЗУЛЬТАТ
# ==========================================

if st.session_state.rm_recognized:

    st.markdown("---")
    st.markdown("## ⭐ Твой результат")

    st.info(
        st.session_state.rm_recognized
    )

    score = st.session_state.rm_score

    st.metric(
        "Сходство с оригиналом",
        f"{score:.1f}%"
    )

    if st.session_state.rm_unlocked:

        st.markdown("""
        <div class="reward-card">
            <div class="reward-stars">⭐ ⭐ ⭐</div>
            <div class="reward-title">
                Ты большой молодец!
            </div>
            <p>Эпизод успешно пройден!</p>
        </div>
        """, unsafe_allow_html=True)

    else:

        st.warning(
            "Попробуй ещё раз. Ты обязательно справишься!"
        )


# ==========================================
# РЕЗЕРВНАЯ КНОПКА
# ==========================================

if not st.session_state.rm_unlocked:

    st.markdown("---")

    if st.button(
        "📖 Я дочитал!",
        key=f"rm_manual_{index}",
        use_container_width=True
    ):

        st.session_state.rm_unlocked = True
        st.rerun()


# ==========================================
# ЗАВЕРШЕНИЕ ЭПИЗОДА
# ==========================================

if st.session_state.rm_unlocked:

    st.markdown("---")

    st.markdown("""
    <div class="reward-card">
        <div class="reward-stars">🌟 🐷 🌟</div>
        <div class="reward-title">
            Новая история ждёт тебя!
        </div>
        <p>Ты открыл следующий этап приключения.</p>
        <p>Мультфильмы добавим на следующем этапе разработки.</p>
    </div>
    """, unsafe_allow_html=True)

    if index < len(episodes) - 1:

        if st.button(
            "Следующая страница ➡️",
            type="primary",
            use_container_width=True,
            key=f"rm_next_{index}"
        ):

            if index not in st.session_state.rm_completed:
                st.session_state.rm_completed.append(index)

            st.session_state.rm_episode += 1
            st.session_state.rm_unlocked = False
            st.session_state.rm_recognized = ""
            st.session_state.rm_score = 0

            st.rerun()

    else:

        st.balloons()

        st.markdown("## 🏆 Ты прочитал всю сказку!")

        st.success(
            "Поздравляем! Три поросёнка благодарят тебя!"
        )

        if st.button(
            "❤️ Прочитать ещё раз",
            use_container_width=True
        ):

            st.session_state.rm_episode = 0
            st.session_state.rm_unlocked = False
            st.session_state.rm_recognized = ""
            st.session_state.rm_score = 0
            st.session_state.rm_completed = []

            st.rerun()


# ==========================================
# ПОДВАЛ
# ==========================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#B49AA5;">
        ReadMotion © 2026<br>
        Маленькие читатели — большие приключения ❤️
    </div>
    """,
    unsafe_allow_html=True
)

# Исправление: скрываем неиспользуемый параметр приложения
