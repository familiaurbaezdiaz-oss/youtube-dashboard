# -*- coding: utf-8 -*-

# ============================================================
# PARTE 1: agregar endpoints proxy en server.js
# ============================================================
path_server = r"C:\Users\hanse\Downloads\railway_dashboard\server.js"

with open(path_server, encoding="utf-8") as f:
    server_content = f.read()

marcador_listen = "app.listen(PORT, () => {"

endpoints_nuevos = '''// Proxy hacia YouTube Data API v3. La clave vive solo aqui, en el
// servidor (variable de entorno YOUTUBE_API_KEY), nunca en el HTML
// que es publico en GitHub.
const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY || "";

app.get('/api/youtube/canal-stats', async (req, res) => {
    const { canal_id } = req.query;
    if (!canal_id) return res.json({ success: false, error: "Falta canal_id" });
    try {
        const r = await fetch(`https://www.googleapis.com/youtube/v3/channels?part=statistics&id=${canal_id}&key=${YOUTUBE_API_KEY}`);
        const d = await r.json();
        const s = d.items?.[0]?.statistics || {};
        res.json({
            success: true,
            suscriptores: parseInt(s.subscriberCount || 0),
            vistas: parseInt(s.viewCount || 0),
            videos: parseInt(s.videoCount || 0)
        });
    } catch (e) {
        res.json({ success: false, error: e.message });
    }
});

app.get('/api/youtube/comentarios-recientes', async (req, res) => {
    const { canal_id } = req.query;
    if (!canal_id) return res.json({ success: false, error: "Falta canal_id" });
    try {
        const rV = await fetch(`https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=${canal_id}&maxResults=5&order=date&type=video&key=${YOUTUBE_API_KEY}`);
        const dV = await rV.json();
        const videos = dV.items || [];
        let todos = [];
        for (const v of videos.slice(0, 3)) {
            const vid = v.id.videoId;
            if (!vid) continue;
            const rC = await fetch(`https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId=${vid}&maxResults=5&order=time&key=${YOUTUBE_API_KEY}`);
            const dC = await rC.json();
            if (dC.items) dC.items.forEach(item => {
                const c = item.snippet.topLevelComment.snippet;
                todos.push({
                    id: item.id, videoId: vid,
                    videoTitulo: v.snippet.title,
                    autor: c.authorDisplayName,
                    texto: c.textDisplay,
                    likes: c.likeCount,
                    fecha: new Date(c.publishedAt).toLocaleDateString('es-DO'),
                    timestamp: new Date(c.publishedAt).getTime()
                });
            });
        }
        todos.sort((a, b) => b.timestamp - a.timestamp);
        res.json({ success: true, comentarios: todos });
    } catch (e) {
        res.json({ success: false, error: e.message });
    }
});

app.listen(PORT, () => {'''

if marcador_listen not in server_content:
    print("ERROR: no se encontro el marcador app.listen en server.js")
else:
    server_content = server_content.replace(marcador_listen, endpoints_nuevos, 1)
    with open(path_server, "w", encoding="utf-8") as f:
        f.write(server_content)
    print("OK: endpoints agregados a server.js")

# ============================================================
# PARTE 2: actualizar index.html para usar los endpoints propios
# ============================================================
path_html = r"C:\Users\hanse\Downloads\railway_dashboard\public\index.html"

with open(path_html, encoding="utf-8") as f:
    html_content = f.read()

vieja_canal_stats = '''async function fetchCanalStats(canal) {
    const r = await fetch(`https://www.googleapis.com/youtube/v3/channels?part=statistics&id=${canal.id}&key=${API_KEY}`);
    const d = await r.json();
    const s = d.items?.[0]?.statistics||{};
    return {...canal, suscriptores:parseInt(s.subscriberCount||0), vistas:parseInt(s.viewCount||0), videos:parseInt(s.videoCount||0)};
}'''

nueva_canal_stats = '''async function fetchCanalStats(canal) {
    const r = await fetch(`/api/youtube/canal-stats?canal_id=${canal.id}`);
    const d = await r.json();
    if (!d.success) return {...canal, suscriptores:0, vistas:0, videos:0};
    return {...canal, suscriptores:d.suscriptores, vistas:d.vistas, videos:d.videos};
}'''

if vieja_canal_stats not in html_content:
    print("ERROR: no se encontro fetchCanalStats viejo en index.html")
else:
    html_content = html_content.replace(vieja_canal_stats, nueva_canal_stats, 1)
    print("OK: fetchCanalStats actualizado")

vieja_comentarios_inicio = '''        const rV = await fetch(`https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=${canalId}&maxResults=5&order=date&type=video&key=${API_KEY}`);
        const dV = await rV.json();
        const videos = dV.items||[];
        let todos = [];
        for(const v of videos.slice(0,3)){
            const vid=v.id.videoId; if(!vid) continue;
            const rC = await fetch(`https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId=${vid}&maxResults=5&order=time&key=${API_KEY}`);
            const dC = await rC.json();
            if(dC.items) dC.items.forEach(item=>{
                const c=item.snippet.topLevelComment.snippet;
                todos.push({
                    id:item.id, videoId:vid,
                    videoTitulo:v.snippet.title,
                    autor:c.authorDisplayName,
                    texto:c.textDisplay,
                    likes:c.likeCount,
                    fecha:new Date(c.publishedAt).toLocaleDateString('es-DO'),
                    timestamp: new Date(c.publishedAt).getTime()
                });
            });
        }
        todos.sort((a,b)=>b.timestamp-a.timestamp);
        return todos;'''

nueva_comentarios = '''        const r = await fetch(`/api/youtube/comentarios-recientes?canal_id=${canalId}`);
        const d = await r.json();
        if (!d.success) return [];
        return d.comentarios;'''

if vieja_comentarios_inicio not in html_content:
    print("ERROR: no se encontro el bloque de comentarios viejo en index.html")
else:
    html_content = html_content.replace(vieja_comentarios_inicio, nueva_comentarios, 1)
    print("OK: fetchComentariosRecientes actualizado")

# Eliminar la linea de la API_KEY del HTML, ya no se necesita
vieja_apikey_linea = 'const API_KEY = "AIzaSyCnvYmEePkUpdGm4lc7wcRuKnYAXojq07Y";\\n'
if vieja_apikey_linea in html_content:
    html_content = html_content.replace(vieja_apikey_linea, '', 1)
    print("OK: linea de API_KEY eliminada del HTML")
else:
    print("AVISO: no se encontro la linea exacta de API_KEY para eliminar (puede que ya no exista o tenga formato distinto, revisar manualmente)")

with open(path_html, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Archivos guardados")
