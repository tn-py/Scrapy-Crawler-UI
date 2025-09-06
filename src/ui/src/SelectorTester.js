
import React, { useState } from 'react';
import axios from 'axios';

const SelectorTester = () => {
    const [url, setUrl] = useState('');
    const [selectors, setSelectors] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleDiscoverSelectors = async () => {
        setLoading(true);
        setError(null);
        setSelectors([]);
        try {
            const response = await axios.get(`http://127.0.0.1:8000/selector/discover?url=${encodeURIComponent(url)}`);
            if (response.data.error) {
                setError(response.data.error);
            } else {
                setSelectors(response.data.selectors);
            }
        } catch (err) {
            setError(err.message);
        }
        setLoading(false);
    };

    return (
        <div>
            <h2>Selector Discoverer</h2>
            <div>
                <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="Enter URL"
                />
                <button onClick={handleDiscoverSelectors} disabled={loading}>
                    {loading ? 'Discovering...' : 'Discover Selectors'}
                </button>
            </div>
            {error && (
                <div>
                    <h3>Error</h3>
                    <p>{error}</p>
                </div>
            )}
            {selectors.length > 0 && (
                <div>
                    <h3>Discovered Selectors</h3>
                    <ul>
                        {selectors.map((item, index) => (
                            <li key={index}>
                                <strong>{item.selector}</strong>: <em>{item.data}</em>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default SelectorTester;
