document.addEventListener('DOMContentLoaded', () => {
    // Initialize Feather icons natively
    feather.replace();

    /**
     * I18N (Internationalization) Logic
     */
    const defaultLang = 'pt-BR';
    const savedLang = localStorage.getItem('unser_haus_lang') || defaultLang;
    
    const btnPt = document.getElementById('btn-lang-pt');
    const btnEn = document.getElementById('btn-lang-en');
    
    function setLanguage(lang) {
        // Save to LocalStorage
        localStorage.setItem('unser_haus_lang', lang);
        
        // Update Buttons
        if (lang === 'pt-BR') {
            btnPt.classList.add('active');
            btnEn.classList.remove('active');
        } else {
            btnEn.classList.add('active');
            btnPt.classList.remove('active');
        }

        // Apply translations using global `i18nDictionary` defined in translations.js
        const dict = i18nDictionary[lang];
        if (!dict) return;

        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (dict[key]) {
                el.textContent = dict[key];
            }
        });
        
        // Trigger clock update to immediately fix the localized date language
        updateClock(lang);
    }
    
    btnPt.addEventListener('click', () => setLanguage('pt-BR'));
    btnEn.addEventListener('click', () => setLanguage('en'));

    /**
     * Update Clock and Date Routine
     */
    function updateClock(forceLang = null) {
        const now = new Date();
        
        // Format Time (HH:MM)
        const timeElement = document.getElementById('time');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        timeElement.textContent = `${hours}:${minutes}`;
        
        // Format Date (Weekday, Day Month Year)
        const dateElement = document.getElementById('date');
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        
        const currentLang = forceLang || localStorage.getItem('unser_haus_lang') || defaultLang;
        // JS Date Locale requires generic codes depending on the browser (using standard BCP 47)
        const localeCode = currentLang === 'pt-BR' ? 'pt-BR' : 'en-US';
        
        let dateString = now.toLocaleDateString(localeCode, options);
        
        // Capitalize the first letter
        dateString = dateString.charAt(0).toUpperCase() + dateString.slice(1);
        dateElement.textContent = dateString;
    }

    // Call once to prevent delay, then initialize loop
    setLanguage(savedLang);
    setInterval(() => updateClock(), 1000);
});
