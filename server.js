const express = require('express');
const path = require('path');
const { exec } = require('child_process');
const fs = require('fs');
 
const app = express();
const PORT = process.env.PORT || 3000;
 
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));
 
const CANALES_CONFIG = {
    "UCtCF9WMqwa5vCjgLNyx5zaw": { carpeta: "fitsecrets",          nombre: "Fit Tips Latino" },
    "UCbRqsnb4vOGQtEW5JDtDE6Q": { carpeta: "content-bot",         nombre: "Un Cafe con el Mundo" },
    "UCbebqeZeD8WdSZypfxb7Tnw": { carpeta: "comohacer",           nombre: "Como Hacer Dinero" },
    "UC7uB3kv6xkRnzBqOuYK0rVQ": { carpeta: "finanzasinlimites",   nombre: "Finanzas Sin Limites" },
    "UCVdxFnplEkh8rs_L9GSCFaw": { carpeta: "dinerosimentiras",    nombre: "Dinero Sin Mentiras" },
    "UCMeGTxwHiUHZV7F6fFS12Qw": { carpeta: "mentedigital",        nombre: "Mente Digital" },
    "UCT1irBNP1JR5O0UD1gcfbOA": { carpeta: "inverteyliberate",    nombre: "Invierte y Liberate" },
    "UCz6JMCRoZTqZNTAPRd7alDQ": { carpeta: "secretosdesalud",     nombre: "Secretos de Salud" },
    "UCN8GZhEYvJXdIkXpoBLfY4w": { carpeta: "comemueveteysana",    nombre: "Come Muevete y Sana" },
    "UC-OLqHHiL9EwKBNFjr8uNEQ": { carpeta: "deportedominicanos",  nombre: "Deporte Dominicanos Sin Fronteras" },
    "UCefqr_OtXH0c8yvOIuSIs8g": { carpeta: "feyabundancia",       nombre: "Fe y Abundancia" },
    "UCrHdus3_spVg2fYDAuE97AQ": { carpeta: "historiacensura",     nombre: "Historia Sin Censura" },
    "UCBg1Ilkd_rOXd98BFwtllhA": { carpeta: "mentalidadganadora",  nombre: "Mentalidad Ganadora" },
    "UCDwuOde7WNjvRzVFTAPDLfQ": { carpeta: "crianzareal",         nombre: "Crianza Real" },
    "UCv6vYEGZkvQLJP22N0VVXrA": { carpeta: "tuproductividad",     nombre: "tu.Productividad" },
    "UCJtuIFNfcNFvRBlEu2cRkJw": { carpeta: "psicologiasinfiltros",nombre: "Psicologia Sin Filtros" },
};
 
const BASE = "C:\\Users\\hanse\\Desktop\\PROYECTOS";
const PYTHON_GLOBAL = "C:\\Users\\hanse\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe";
 
app.post('/api/generar-video', (req, res) => {
    const { canal_id, modo, contenido } = req.body;
    if (!canal_id || !contenido || !modo) {
        return res.json({ success: false, error: "Faltan parametros" });
    }
    const config = CANALES_CONFIG[canal_id];
    if (!config) {
        return res.json({ success: false, error: "Canal no encontrado" });
    }
 
    const carpeta = `${BASE}\\${config.carpeta}`;
    const contenidoEscapado = contenido
        .replace(/\\/g, '\\\\')
        .replace(/"/g, '\\"')
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '');
 
    const scriptPy = `import os, sys
sys.path.insert(0, r"${carpeta}")
os.chdir(r"${carpeta}")
from dotenv import load_dotenv
load_dotenv()
from modules.script_generator import generar_script, extraer_imagenes_del_script, generar_titulo_gancho
from modules.voice_generator import generar_audio
from modules.video_generator import generar_video_multitema
from modules.music_generator import obtener_musica_fondo
from modules.youtube_uploader import subir_video, generar_titulo_y_descripcion
from modules.thumbnail_generator import crear_thumbnail
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
from datetime import datetime
 
main_content = open(r"${carpeta}\\main.py", encoding='utf-8').read()
COLOR_CANAL = main_content.split('COLOR_CANAL = "')[1].split('"')[0]
import re
logo_match = re.search(r'LOGO_CANAL\\s*=\\s*r?"([^"]+)"', main_content)
LOGO_CANAL = logo_match.group(1) if logo_match else ""
NOMBRE_CANAL = "${config.nombre}"
modo = "${modo}"
contenido = "${contenidoEscapado}"
 
print(f"Iniciando pipeline para {NOMBRE_CANAL} - modo: {modo}", flush=True)
 
if modo == "idea":
    resultado = generar_script(contenido, "short")
    script = resultado['script']
else:
    script = contenido
 
tema = contenido[:80]
ruta_audio = generar_audio(script)
if not ruta_audio:
    print("ERROR: No se pudo generar audio", flush=True)
    sys.exit(1)
 
busquedas = extraer_imagenes_del_script(script, tema)
ruta_video = generar_video_multitema(busquedas, ruta_audio)
if not ruta_video:
    print("ERROR: No se pudo generar video", flush=True)
    sys.exit(1)
 
ruta_musica = obtener_musica_fondo()
if ruta_musica:
    voz = AudioFileClip(ruta_audio)
    musica = AudioFileClip(ruta_musica).with_effects([]).with_volume_scaled(0.15)
    video = VideoFileClip(ruta_video)
    if musica.duration > video.duration:
        musica = musica.subclipped(0, video.duration)
    audio_final = CompositeAudioClip([voz, musica])
    video_clip = video.with_audio(audio_final)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta_final = f"outputs/video_manual_{ts}.mp4"
    video_clip.write_videofile(ruta_final, fps=24, codec="libx264", audio_codec="aac", logger=None)
else:
    ruta_final = ruta_video
 
titulo_gancho = generar_titulo_gancho(script, tema)
ruta_thumbnail = crear_thumbnail(titulo=titulo_gancho, nombre_canal=NOMBRE_CANAL, logo_path=LOGO_CANAL, color_canal=COLOR_CANAL)
titulo, descripcion = generar_titulo_y_descripcion(tema, script, titulo_gancho)
video_id = subir_video(ruta_final, titulo, descripcion, ruta_thumbnail=ruta_thumbnail, tema=tema)
if video_id:
    print(f"SUCCESS:{video_id}", flush=True)
else:
    print("ERROR: No se pudo subir", flush=True)
`;
 
    const tempFile = `${BASE}\\temp_video_${Date.now()}.py`;
    fs.writeFileSync(tempFile, scriptPy, 'utf8');
    console.log(`Generando video para ${config.nombre} - modo: ${modo}`);
 
    res.json({ 
        success: true, 
        message: "Video en proceso — aparecera en YouTube en 3-5 minutos", 
        url: `https://studio.youtube.com/channel/${canal_id}/videos` 
    });
 
    exec(`"${PYTHON_GLOBAL}" "${tempFile}"`, { cwd: carpeta, timeout: 600000, env: { ...process.env, PYTHONIOENCODING: 'utf-8' } }, (err, stdout, stderr) => {
        if (err) {
            console.error(`Error ${config.nombre}:`, err.message);
            if (stderr) console.error('STDERR COMPLETO:', stderr);
            if (stdout) console.error('STDOUT COMPLETO:', stdout);
        } else {
            const ok = stdout.split('\n').find(l => l.startsWith('SUCCESS:'));
            if (ok) {
                const videoId = ok.replace('SUCCESS:', '').trim();
                console.log(`Video publicado ${config.nombre}: https://youtube.com/shorts/${videoId}`);
            } else {
                console.log(`Output: ${stdout.substring(0, 500)}`);
            }
        }
        
        // // try { fs.unlinkSync(tempFile); } catch(e) {}
    });
});
 
app.listen(PORT, () => {
    console.log(`Dashboard corriendo en puerto ${PORT}`);
});
 