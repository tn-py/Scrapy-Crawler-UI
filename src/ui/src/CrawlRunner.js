
import React, { useState } from 'react';
import axios from 'axios';

const CrawlRunner = () => {
    const [spider, setSpider] = useState('');
    const [stdout, setStdout] = useState('');
    const [stderr, setStderr] = useState('');
    const [error, setError] = useState(null);

    const handleCrawlRun = async () => {
        try {
            const response = await axios.post(`http://127.0.0.1:8000/crawl/run?spider=${spider}`);
            setStdout(response.data.stdout);
            setStderr(response.data.stderr);
            setError(null);
        } catch (err) {
            setError(err.message);
            setStdout('');
            setStderr('');
        }
    };

    return (
        <div>
            <h2>Crawl Runner</h2>
            <div>
                <input
                    type="text"
                    value={spider}
                    onChange={(e) => setSpider(e.target.value)}
                    placeholder="Enter Spider Name"
                />
                <button onClick={handleCrawlRun}>Run Crawl</button>
            </div>
            {stdout && (
                <div>
                    <h3>Stdout</h3>
                    <pre>{stdout}</pre>
                </div>
            )}
            {stderr && (
                <div>
                    <h3>Stderr</h3>
                    <pre>{stderr}</pre>
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

export default CrawlRunner;
