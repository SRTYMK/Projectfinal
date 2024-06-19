import React, { useState } from 'react';

const SearchBar = () => {
    const [searchTerm, setSearchTerm] = useState('');

    const handleInputChange = (event) => {
        setSearchTerm(event.target.value);
    };

    const handleSearch = () => {
        // ฟังก์ชันการค้นหา สามารถปรับแต่งตามความต้องการได้
        console.log('Searching for:', searchTerm);
    };

    return (
        <div className="search-bar">
            <input
                type="text"
                placeholder="ค้นหาเมล็ดพันธุ์"
                value={searchTerm}
                onChange={handleInputChange}
            />
            <button onClick={handleSearch}>ค้นหา</button>
        </div>
    );
};

export default SearchBar;
