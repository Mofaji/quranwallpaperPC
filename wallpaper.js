const updateInterval = 1800000; // 30 minutes

async function fetchRandomVerse() {
    try {
        const response = await fetch('https://api.alquran.cloud/v1/ayah/random', {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data.data;
    } catch (error) {
        console.error('Error fetching verse:', error);
        document.getElementById('arabic').textContent = 'Failed to load verse';
        document.getElementById('translation').textContent = 'Please check your internet connection';
        document.getElementById('info').textContent = 'Error occurred';
        return null;
    }
}

async function updateWallpaper() {
    const verse = await fetchRandomVerse();
    if (!verse) return;

    try {
        document.getElementById('arabic').textContent = verse.text;
        document.getElementById('translation').textContent = verse.translation.en;
        document.getElementById('info').textContent = `Surah ${verse.surah.englishName} (${verse.surah.number}:${verse.numberInSurah})`;
    } catch (error) {
        console.error('Error updating DOM:', error);
    }
}

async function getRandomBackground() {
    try {
        const response = await fetch('https://api.unsplash.com/photos/random?query=nature,landscape,mountains&client_id=oZQma7v_znVRCBBdlJt5jwPwuyt2O4DfYHL350hq_rA');
        const data = await response.json();
        return data.urls.regular;
    } catch (error) {
        console.error('Error fetching background:', error);
        return 'https://images.unsplash.com/photo-1506744038136-46273834b3fb';
    }
}

async function getRandomAyat() {
    try {
        const surah = Math.floor(Math.random() * 114) + 1;
        const response = await fetch(`https://api.alquran.cloud/v1/surah/${surah}`);
        const data = await response.json();
        
        if (!data.data || !data.data.ayahs || data.data.ayahs.length === 0) {
            throw new Error('Invalid API response');
        }

        const randomAyahIndex = Math.floor(Math.random() * data.data.ayahs.length);
        const ayah = data.data.ayahs[randomAyahIndex];
        
        const [translationResponse, transliterationResponse] = await Promise.all([
            fetch(`https://api.alquran.cloud/v1/ayah/${ayah.number}/en.sahih`),
            fetch(`https://api.alquran.cloud/v1/ayah/${ayah.number}/en.transliteration`)
        ]);
        
        const translationData = await translationResponse.json();
        const transliterationData = await transliterationResponse.json();

        let arabicText = ayah.text;
        const bismillahVariants = [
            'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ',
            'بِّسۡمِ ٱللَّهِ ٱلرَّحۡمَـٰنِ ٱلرَّحِیمِ',
            'بِسْمِ اللَّٰهِ الرَّحْمَٰنِ الرَّحِيمِ',
            'بِسۡمِ ٱللَّهِ ٱلرَّحۡمَٰنِ ٱلرَّحِيمِ',
            'بِسۡمِ ٱللَّهِ ٱلرَّحۡمَـٰنِ ٱلرَّحِیمِ'
        ];
        
        bismillahVariants.forEach(variant => {
            arabicText = arabicText.replace(variant, '').trim();
        });

        return {
            arabic: arabicText,
            translation: translationData.data.text,
            info: `Quran ${surah}:${ayah.numberInSurah}`,
            transcription: transliterationData.data.text
        };
    } catch (error) {
        console.error('Error fetching ayat:', error);
        return {
            arabic: 'Error loading verse',
            translation: 'Please try again',
            info: 'Error',
            transcription: 'Error loading verse'
        };
    }
}

// Update content immediately when loaded
updateContent();

async function updateContent() {
    try {
        const [background, ayat] = await Promise.all([
            getRandomBackground(),
            getRandomAyat()
        ]);

        document.querySelector('.wallpaper-container').style.backgroundImage = `url('${background}')`;
        document.getElementById('arabic').textContent = ayat.arabic;
        document.getElementById('translation').textContent = ayat.translation;
        document.getElementById('info').textContent = ayat.info;
    } catch (error) {
        console.error('Error updating content:', error);
    }
}

// Initial update
document.addEventListener('DOMContentLoaded', updateContent);

// Update periodically
setInterval(updateWallpaper, updateInterval);