const R = 6371000;
const toRad = (d) => (d * Math.PI) / 180;

function haversine(a, b) { // a, b = [lng, lat]
    const dLat = toRad(b[1] - a[1]);
    const dLng = toRad(b[0] - a[0]);
    const h =
        Math.sin(dLat / 2) ** 2 +
        Math.cos(toRad(a[1])) * Math.cos(toRad(b[1])) * Math.sin(dLng / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(h));
}

// Heap mínimo simples para o Dijkstra
class MinHeap {
    constructor() { this.a = []; }
    push(item) {
        const a = this.a;
        a.push(item);
        let i = a.length - 1;
        while (i > 0) {
            const p = (i - 1) >> 1;
            if (a[p][0] <= a[i][0]) break;
            [a[p], a[i]] = [a[i], a[p]];
            i = p;
        }
    }
    pop() {
        const a = this.a;
        const top = a[0];
        const last = a.pop();
        if (a.length) {
            a[0] = last;
            let i = 0;
            for (;;) {
                let l = 2 * i + 1, r = l + 1, m = i;
                if (l < a.length && a[l][0] < a[m][0]) m = l;
                if (r < a.length && a[r][0] < a[m][0]) m = r;
                if (m === i) break;
                [a[m], a[i]] = [a[i], a[m]];
                i = m;
            }
        }
        return top;
    }
    get size() { return this.a.length; }
}

// Extrai todas as linhas ([[lng,lat], ...]) do GeoJSON
function extractLines(geojson) {
    const lines = [];
    const feats = geojson.type === "FeatureCollection" ? geojson.features : [geojson];
    feats.forEach((f) => {
        const g = f.geometry || f;
        if (g.type === "LineString") lines.push(g.coordinates);
        if (g.type === "MultiLineString") g.coordinates.forEach((l) => lines.push(l));
    });
    return lines;
}

/**
 * @param geojson   o GeoJSON da rodovia
 * @param risk      array onde o índice = km
 * @param kmOffset  ajuste fino (km real do ponto de origem)
 * @param snapMeters distância para ligar as duas pistas
 */
export function buildRiskSegments(geojson, risk, { kmOffset = 0, snapMeters = 150, maxGapMeters = 5000 } = {}) {
    const lines = extractLines(geojson);

    // 1) nós
    const nodeIndex = new Map();
    const coords = [];
    const lineIds = lines.map((line) =>
        line.map((c) => {
            const key = `${c[0]},${c[1]}`;
            if (!nodeIndex.has(key)) {
                nodeIndex.set(key, coords.length);
                coords.push(c);
            }
            return nodeIndex.get(key);
        })
    );

    // 2) arestas
    const adj = coords.map(() => []);
    const link = (a, b) => {
        const w = haversine(coords[a], coords[b]);
        adj[a].push([b, w]);
        adj[b].push([a, w]);
    };

    lineIds.forEach((ids) => {
        for (let i = 0; i < ids.length - 1; i++) {
            if (ids[i] !== ids[i + 1]) link(ids[i], ids[i + 1]);
        }
    });

    // ligações por proximidade (une as duas pistas)
    const CELL = 0.002; // ~200 m
    const grid = new Map();
    const cellKey = (c) => `${Math.floor(c[0] / CELL)},${Math.floor(c[1] / CELL)}`;
    coords.forEach((c, id) => {
        const k = cellKey(c);
        if (!grid.has(k)) grid.set(k, []);
        grid.get(k).push(id);
    });
    coords.forEach((c, id) => {
        const cx = Math.floor(c[0] / CELL);
        const cy = Math.floor(c[1] / CELL);
        for (let dx = -1; dx <= 1; dx++) {
            for (let dy = -1; dy <= 1; dy++) {
                (grid.get(`${cx + dx},${cy + dy}`) || []).forEach((other) => {
                    if (other > id && haversine(c, coords[other]) <= snapMeters) link(id, other);
                });
            }
        }
    });

    // 2.5) une as "ilhas" desconectadas pelas pontas mais próximas
    const parent = coords.map((_, i) => i);
    const find = (x) => {
        while (parent[x] !== x) {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        return x;
    };
    const union = (a, b) => { parent[find(a)] = find(b); };

    adj.forEach((edges, u) => edges.forEach(([v]) => union(u, v)));

    const endpoints = [];
    lineIds.forEach((ids) => {
        if (ids.length > 1) endpoints.push(ids[0], ids[ids.length - 1]);
    });
    const ends = [...new Set(endpoints)];

    const pairs = [];
    for (let i = 0; i < ends.length; i++) {
        for (let j = i + 1; j < ends.length; j++) {
            pairs.push([haversine(coords[ends[i]], coords[ends[j]]), ends[i], ends[j]]);
        }
    }
    pairs.sort((x, y) => x[0] - y[0]);

    for (const [d, a, b] of pairs) {
        if (d > maxGapMeters) break;
        if (find(a) !== find(b)) {
            link(a, b);
            union(a, b);
        }
    }

    // 3) Dijkstra a partir do ponto mais ao sul (São Paulo, km 0)
    let origin = 0;
    coords.forEach((c, i) => { if (c[1] < coords[origin][1]) origin = i; });

    const dist = new Array(coords.length).fill(Infinity);
    dist[origin] = 0;
    const heap = new MinHeap();
    heap.push([0, origin]);
    while (heap.size) {
        const [d, u] = heap.pop();
        if (d > dist[u]) continue;
        for (const [v, w] of adj[u]) {
            if (d + w < dist[v]) {
                dist[v] = d + w;
                heap.push([dist[v], v]);
            }
        }
    }

    // 4) um segmento por par de pontos, com risco interpolado entre os km vizinhos
    const riskAt = (kmFloat) => {
        // trata o risco de cada km como valor no CENTRO do km (km + 0.5)
        const x = kmFloat - 0.5;
        const i0 = Math.floor(x);
        const i1 = i0 + 1;
        const r0 = risk[Math.max(0, Math.min(risk.length - 1, i0))];
        const r1 = risk[Math.max(0, Math.min(risk.length - 1, i1))];
        if (r0 == null || r1 == null) return r0 ?? r1 ?? null;
        const t = x - i0;
        return r0 + (r1 - r0) * t;
    };

    const features = [];
    lineIds.forEach((ids) => {
        for (let i = 0; i < ids.length - 1; i++) {
            const a = ids[i], b = ids[i + 1];
            if (!isFinite(dist[a]) || !isFinite(dist[b])) continue;

            const kmFloat = (dist[a] + dist[b]) / 2 / 1000 + kmOffset;
            features.push({
                type: "Feature",
                properties: {
                    km: Math.floor(kmFloat),
                    risco: riskAt(kmFloat),
                },
                geometry: { type: "LineString", coordinates: [coords[a], coords[b]] },
            });
        }
    });

    return { type: "FeatureCollection", features };
}

export function riskColor(risco) {
    if (risco == null) return "#999"; // sem dado
    const t = Math.min(Math.max(risco / 10, 0), 1);
    const hue = 50 - 50 * t;          // 50 (amarelo) -> 0 (vermelho)
    const light = 62 - 20 * t;        // fica mais escuro/forte
    return `hsl(${hue}, 95%, ${light}%)`;
}