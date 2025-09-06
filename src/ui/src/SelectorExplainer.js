
import React, { useState } from 'react';
import axios from 'axios';

const SelectorExplainer = () => {
    const [selector, setSelector] = useState('');
    const [explanation, setExplanation] = useState('');
    const [error, setError] = useState(null);

    const handleExplainSelector = async () => {
        try {
            const response = await axios.get(`http://127.0.0.1:8000/selector/explain?selector=${selector}`);
            setExplanation(response.data.explanation);
            setError(null);
        } catch (err) {
            setError(err.message);
            setExplanation('');
        }
    };

    return (
        <div>
            <h2>Selector Explainer</h2>
            <div>
                <input
                    type="text"
                    value={selector}
                    onChange={(e) => setSelector(e.target.value)}
                    placeholder="Enter Selector"
                />
                <button onClick={handleExplainSelector}>Explain Selector</button>
            </div>
            {explanation && (
                <div>
                    <h3>Explanation</h3>
                    <p>{explanation}</p>
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

export default SelectorExplainer;
