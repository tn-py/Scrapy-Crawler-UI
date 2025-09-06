
import React, { useState } from 'react';
import axios from 'axios';

const SelectorRepairer = () => {
    const [url, setUrl] = useState('');
    const [selector, setSelector] = useState('');
    const [suggestion, setSuggestion] = useState('');
    const [error, setError] = useState(null);

    const handleRepairSelector = async () => {
        try {
            const response = await axios.get(`http://127.0.0.1:8000/selector/repair?url=${url}&selector=${selector}`);
            setSuggestion(response.data.suggestion);
            setError(null);
        } catch (err) {
            setError(err.message);
            setSuggestion('');
        }
    };

    return (
        <div>
            <h2>Selector Repairer</h2>
            <div>
                <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="Enter URL"
                />
                <input
                    type="text"
                    value={selector}
                    onChange={(e) => setSelector(e.target.value)}
                    placeholder="Enter Selector"
                />
                <button onClick={handleRepairSelector}>Repair Selector</button>
            </div>
            {suggestion && (
                <div>
                    <h3>Suggestion</h3>
                    <p>{suggestion}</p>
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

export default SelectorRepairer;
