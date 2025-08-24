import React, { useState } from 'react';
import axios from 'axios';

const UrlTester = () => {
    const [url, setUrl] = useState('');
    const [render, setRender] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleTestUrl = async () => {
        try {
            const response = await axios.get(`http://127.0.0.1:8000/url/test?url=${url}&render=${render}`);
            setResult(response.data);
            setError(null);
        } catch (err) {
            setError(err.message);
            setResult(null);
        }
    };

    return (
        <div>
            <h2>URL Tester</h2>
            <div>
                <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="Enter URL"
                />
                <label>
                    <input
                        type="checkbox"
                        checked={render}
                        onChange={(e) => setRender(e.target.checked)}
                    />
                    Render JavaScript
                </label>
                <button onClick={handleTestUrl}>Test URL</button>
            </div>
            {result && (
                <div>
                    <h3>Result</h3>
                    <p>Status: {result.status}</p>
                    <p>Latency: {result.latency.toFixed(2)} seconds</p>
                    <p>Charset: {result.charset}</p>
                </div>
            )}
            {error && (
                <div>
                    <h3>Error</h3>
                    <p>{error}</p>
                </div>
            )}
        </div>
    );
};

export default UrlTester;