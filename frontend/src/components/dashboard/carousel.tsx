import React from 'react';

const Carousel = () => {
return(
    <div className="image-carousel">
                    <div className="carousel-title">
                        🖼️ Imágenes del Estudio
                    </div>
                    <div className="carousel-container">
                        <div className="carousel-image active">📷</div>
                        <div className="carousel-image">📸</div>
                        <div className="carousel-image">🎯</div>
                        <div className="carousel-image">🔍</div>
                    </div>
                </div>
)
};

export default Carousel;