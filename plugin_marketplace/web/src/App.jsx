import { useEffect, useState } from 'react';

export default function App() {
  const [plugins, setPlugins] = useState([]);
  const [search, setSearch] = useState('');
  const [downloads, setDownloads] = useState({});

  useEffect(() => {
    fetch('/plugins')
      .then(r => r.json())
      .then(setPlugins)
      .catch(() => {});
    fetch('/metrics')
      .then(r => r.text())
      .then(text => {
        const counts = {};
        const regex = /plugin_downloads_total\{plugin_id="([^\"]+)"\} (\d+)/g;
        let m;
        while ((m = regex.exec(text))) {
          counts[m[1]] = parseInt(m[2], 10);
        }
        setDownloads(counts);
      })
      .catch(() => {});
  }, []);

  const filtered = plugins.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="container">
      <h1>Plugin Marketplace</h1>
      <input
        placeholder="Search"
        value={search}
        onChange={e => setSearch(e.target.value)}
      />
      <ul>
        {filtered.map(p => (
          <li key={p.id}>
            <h3>
              {p.name} ({p.version})
            </h3>
            <p>ID: {p.id}</p>
            {p.dependencies && p.dependencies.length > 0 && (
              <p>Dependencies: {p.dependencies.join(', ')}</p>
            )}
            <p>Downloads: {downloads[p.id] || 0}</p>
            <a href={`/plugins/${p.id}/download`}>Download</a>
          </li>
        ))}
      </ul>
    </div>
  );
}
