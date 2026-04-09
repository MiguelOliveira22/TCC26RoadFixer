export default function RecentAccidents() {
  const reports = [
    { id: 1, local: "BR-116 KM 240", status: "Bloqueado", gravidade: "Alta" },
    { id: 2, local: "BR-101 KM 012", status: "Liberado", gravidade: "Baixa" },
    { id: 3, local: "BR-381 KM 480", status: "Atenção", gravidade: "Média" },
  ];

  return (
    <section style={styles.section}>
      <h2 style={styles.title}>ÚLTIMOS <span style={{color: 'var(--laranja)'}}>RELATOS</span></h2>
      <div style={styles.tableWrapper}>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>LOCALIZAÇÃO</th>
              <th style={styles.th}>STATUS</th>
              <th style={styles.th}>GRAVIDADE</th>
              <th style={styles.th}>AÇÃO</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((r) => (
              <tr key={r.id} style={styles.tr}>
                <td style={styles.td}>{r.local}</td>
                <td style={styles.td}>
                   <span style={{...styles.badge, color: r.status === 'Bloqueado' ? 'var(--laranja)' : '#fff'}}>
                     ● {r.status}
                   </span>
                </td>
                <td style={styles.td}>{r.gravidade}</td>
                <td style={styles.td}><button style={styles.miniBtn}>DETALHES</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

const styles = {
  section: { padding: '60px 5%', backgroundColor: 'var(--preto)' },
  title: { fontSize: '2rem', marginBottom: '30px' },
  tableWrapper: { overflowX: 'auto' },
  table: { width: '100%', borderCollapse: 'collapse', color: '#fff' },
  th: { textAlign: 'left', padding: '15px', borderBottom: '2px solid var(--laranja)', color: '#888', fontSize: '0.8rem' },
  tr: { borderBottom: '1px solid #222', transition: '0.3s' },
  td: { padding: '15px' },
  badge: { fontSize: '0.8rem', fontWeight: 'bold' },
  miniBtn: { 
    backgroundColor: 'transparent', 
    border: '1px solid #444', 
    color: '#fff', 
    padding: '5px 10px', 
    cursor: 'pointer',
    fontSize: '0.7rem'
  }
};