document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const translateBtn = document.getElementById('translate-btn');
    const progressContainer = document.getElementById('progress-container');
    const progressFill = document.getElementById('progress-fill');
    const statusText = document.getElementById('status-text');
    const percentText = document.getElementById('percent-text');

    // i18n Dictionary
    const i18n = {
        es: {
            title: "Traduce tus documentos",
            subtitle: "Especializado en planos eléctricos y documentos técnicos complejos con preservación de diseño original.",
            dropTitle: "Arrastra tus archivos aquí",
            dropSubtitle: "PDF, Word, DXF o imágenes (PNG/JPG)",
            labelTarget: "Idioma de Destino",
            labelFormat: "Formato de Salida",
            labelPrecision: "Modo de Precisión",
            optPdf: "Mismo que original (PDF)",
            optSvg: "Vectorial Editable (.svg)",
            optStandard: "Estándar (Texto fluido)",
            optSchematic: "Esquema Técnico (Layout Exacto)",
            optOcr: "Escaneado (OCR avanzado)",
            btnText: "Comenzar Traducción",
            btnDownload: "Descargar Documento",
            stages: [
                "Analizando estructura vectorial...",
                "Extrayendo capas de texto...",
                "Traduciendo términos técnicos...",
                "Reconstruyendo layout original...",
                "Optimizando PDF de salida...",
                "¡Listo para descargar!"
            ],
            alertNoFile: "Por favor, selecciona un archivo primero.",
            alertSuccess: "Traducción completada con éxito. La copia exacta ha sido generada.",
            filesSelected: "archivo(s) seleccionado(s)"
        },
        en: {
            title: "Translate your documents",
            subtitle: "Specialized in electrical schematics and complex technical documents with original layout preservation.",
            dropTitle: "Drop your files here",
            dropSubtitle: "PDF, Word, DXF or images (PNG/JPG)",
            labelTarget: "Target Language",
            labelFormat: "Output Format",
            labelPrecision: "Precision Mode",
            optPdf: "Same as original (PDF)",
            optSvg: "Editable Vector (.svg)",
            optStandard: "Standard (Flowing text)",
            optSchematic: "Technical Schematic (Exact Layout)",
            optOcr: "Scanned (Advanced OCR)",
            btnText: "Start Translation",
            btnDownload: "Download Document",
            stages: [
                "Analyzing vector structure...",
                "Extracting text layers...",
                "Translating technical terms...",
                "Reconstructing original layout...",
                "Optimizing output PDF...",
                "Ready to download!"
            ],
            alertNoFile: "Please select a file first.",
            alertSuccess: "Translation completed successfully. The exact copy has been generated.",
            filesSelected: "file(s) selected"
        }
    };

    // Detect language
    const userLang = navigator.language.startsWith('es') ? 'es' : 'en';
    const t = i18n[userLang];

    // Apply i18n
    document.getElementById('i18n-title').textContent = t.title;
    document.getElementById('i18n-subtitle').textContent = t.subtitle;
    document.getElementById('i18n-drop-title').textContent = t.dropTitle;
    document.getElementById('i18n-drop-subtitle').textContent = t.dropSubtitle;
    document.getElementById('i18n-label-target').textContent = t.labelTarget;
    document.getElementById('i18n-label-format').textContent = t.labelFormat;
    document.getElementById('i18n-label-precision').textContent = t.labelPrecision;
    document.getElementById('i18n-opt-pdf').textContent = t.optPdf;
    document.getElementById('i18n-opt-svg').textContent = t.optSvg;
    document.getElementById('i18n-opt-standard').textContent = t.optStandard;
    document.getElementById('i18n-opt-schematic').textContent = t.optSchematic;
    document.getElementById('i18n-opt-ocr').textContent = t.optOcr;
    document.getElementById('i18n-btn-text').textContent = t.btnText;
    document.getElementById('i18n-download-text').textContent = t.btnDownload;

    // Drag & Drop events
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('active');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('active');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('active');
        const files = e.dataTransfer.files;
        handleFiles(files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const dropText = document.getElementById('i18n-drop-title');
            const dropSubText = document.getElementById('i18n-drop-subtitle');
            dropText.textContent = `${files.length} ${t.filesSelected}`;
            dropSubText.textContent = Array.from(files).map(f => f.name).join(', ');
            
            // Highlight drop zone
            dropZone.style.borderColor = 'var(--accent)';
            dropZone.style.background = 'rgba(16, 185, 129, 0.05)';
        }
    }

    // API Configuration
    const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : window.location.origin;

    const downloadBtn = document.getElementById('download-btn');
    let downloadLink = "";

    // Translate button logic
    translateBtn.addEventListener('click', async () => {
        const files = fileInput.files;
        if (files.length === 0 && !document.getElementById('i18n-drop-title').textContent.includes(t.filesSelected)) {
            alert(t.alertNoFile);
            return;
        }

        const file = files[0]; // Process first file for now
        const targetLang = document.getElementById('target-lang').value;
        const precisionMode = document.getElementById('precision-mode').value;

        progressContainer.style.display = 'block';
        translateBtn.disabled = true;
        translateBtn.style.opacity = '0.5';

        // Start progress simulation
        let progress = 0;
        const stages = t.stages;
        const interval = setInterval(() => {
            if (progress < 90) {
                progress += Math.random() * 5;
                updateProgress(progress, stages);
            }
        }, 800);

        function updateProgress(val, stageList) {
            progressFill.style.width = `${val}%`;
            percentText.textContent = `${Math.floor(val)}%`;
            const stageIndex = Math.min(Math.floor((val / 100) * stageList.length), stageList.length - 1);
            statusText.textContent = stageList[stageIndex];
        }

        // Try real API call
        const formData = new FormData();
        formData.append('file', file);
        formData.append('target_lang', targetLang);
        formData.append('precision_mode', precisionMode);

        try {
            const response = await fetch(`${API_URL}/translate`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                clearInterval(interval);
                updateProgress(100, stages);
                statusText.style.color = 'var(--accent)';
                
                downloadLink = `${API_URL}${data.download_url}`;
                
                setTimeout(() => {
                    alert(t.alertSuccess);
                    translateBtn.style.display = 'none';
                    downloadBtn.style.display = 'flex';
                }, 500);
            } else {
                throw new Error('Backend error');
            }
        } catch (error) {
            console.log("Backend not reached, falling back to simulation...");
            // Finish simulation if backend fails
            let finishProgress = progress;
            const finishInterval = setInterval(() => {
                finishProgress += 10;
                if (finishProgress >= 100) {
                    finishProgress = 100;
                    clearInterval(finishInterval);
                    clearInterval(interval);
                    updateProgress(100, stages);
                    statusText.style.color = 'var(--accent)';
                    setTimeout(() => {
                        alert(t.alertSuccess + " (Simulado)");
                        translateBtn.style.display = 'none';
                        downloadBtn.style.display = 'flex';
                    }, 500);
                }
                updateProgress(finishProgress, stages);
            }, 200);
        }
    });

    downloadBtn.addEventListener('click', () => {
        if (downloadLink) {
            window.location.href = downloadLink;
        } else {
            alert("No hay archivo listo para descargar (Modo Simulación)");
        }
    });
});
