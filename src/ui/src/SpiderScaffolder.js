
import React, { useState } from 'react';
import axios from 'axios';

const SpiderScaffolder = () => {
    const [name, setName] = useState('');
    const [url, setUrl] = useState('');
    const [selector, setSelector] = useState('');
    const [spiderCode, setSpiderCode] = useState('');
    const [itemCode, setItemCode] = useState('');
    const [error, setError] = useState(null);

    const handleScaffoldSpider = async () => {
        try {
            const response = await axios.get(`http://127.0.0.1:8000/spider/scaffold?name=${name}&url=${url}&selector=${selector}`);
            setSpiderCode(response.data.spider_code);
            setItemCode(response.data.item_code);
            setError(null);
        } catch (err) {
            setError(err.message);
            setSpiderCode('');
            setItemCode('');
        }
    };

    return (
        <div>
            <h2>Spider Scaffolder</h2>
            <div>
                <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter Spider Name"
                />
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
                <button onClick={handleScaffoldSpider}>Scaffold Spider</button>
            </div>
            {spiderCode && itemCode && (
                <div>
                    <h3>Generated Code</h3>
                    <h4>Spider Code</h4>
                    <pre>{spiderCode}</pre>
                    <h4>Item Code</h4>
                    <pre>{itemCode}</pre>
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

export default SpiderScaffolder;
