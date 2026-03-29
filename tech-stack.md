# 🛠️ Başlangıç Seviyesi Kurulum Rehberi: SensoryArch AI

[cite_start]Bu rehber, iç mimarlık projelerini nöro-erişilebilirlik açısından analiz eden uygulamanı en hızlı şekilde ayağa kaldırman için tasarlanmıştır. 

---

## [cite_start]1. Neden Bu Teknolojileri Seçiyoruz? 

* [cite_start]**Python:** Yazımı İngilizce cümle kurmaya en yakın dildir ve yapay zeka projelerinin ana dilidir. 
* [cite_start]**Streamlit:** Karmaşık kodlar bilmene gerek kalmadan, sadece Python ile profesyonel bir web sayfası yapmanı sağlar. 
* [cite_start]**Gemini 1.5 Flash:** Görselleri (fotoğraf, render) bir mimar gibi analiz etme yeteneği çok yüksektir. [cite: 1, 10]

---

## [cite_start]2. Adım Adım Kurulum 

### [cite_start]**Adım 1: Hazırlık** 
1. **Python:** [python.org](https://www.python.org/) sitesinden güncel sürümü indirin. [cite_start]Kurarken **"Add Python to PATH"** kutucuğunu işaretleyin. 
2. [cite_start]**VS Code:** Kodlarını yazacağın programı [code.visualstudio.com](https://code.visualstudio.com/) adresinden kurun. 

### [cite_start]**Adım 2: Proje Klasörü ve Kütüphaneler** 
1. [cite_start]Masaüstünde `SensoryArch` adlı bir klasör oluşturun ve VS Code ile bu klasörü açın. 
2. [cite_start]VS Code terminaline (`Ctrl + J`) şu komutu yazıp Enter'a basın: 
   [cite_start]`pip install streamlit google-generativeai` 

### [cite_start]**Adım 3: Uygulama Kodunu Oluşturma (app.py)** 
[cite_start]Klasöründe `app.py` adında yeni bir dosya oluşturun ve aşağıdaki kodu yapıştırın: 

```python
import streamlit as st
import google.generativeai as genai

# API Yapılandırması (Kendi anahtarını buraya yapıştır)
genai.configure(api_key="BURAYA_ANAHTARINI_YAZ")

st.title("🧠 SensoryArch AI")
st.write("Tasarımını yükle, nöro-erişilebilirlik analizini al.")

# Fotoğraf Yükleme Butonu
dosya = st.file_uploader("Bir iç mekan görseli seç...", type=["jpg", "png", "jpeg"])

if dosya:
    st.image(dosya, caption='Yüklenen Tasarım', use_container_width=True)
    
    if st.button('Analiz Et'):
        with st.spinner('Analiz ediliyor...'):
            model = genai.GenerativeModel('gemini-1.5-flash')
            # AI'ya verilen talimat
            mesaj = "Bir iç mimar gibi bu görseldeki ışık, yansıma ve karmaşa risklerini analiz et."
            cevap = model.generate_content([mesaj, dosya])
            
            st.subheader("Duyusal Analiz Sonucu")
            st.write(cevap.text)