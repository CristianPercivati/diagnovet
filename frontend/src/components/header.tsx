import React from "react";

const Header: React.FC = () => {
  return (
    <header className="bg-gradient-to-r from-gray-800 to-gray-700 text-white !p-6 flex justify-between items-center rounded-t-lg">
      <div className="flex items-center !gap-3">
        <div className="bg-green-500 w-10 h-10 rounded-full flex items-center justify-center text-xl">🐾</div>
        <span className="text-xl font-semibold">DiagnoVET</span>
      </div>
      <div className="flex items-center !gap-3">
        <div className="bg-green-500 w-9 h-9 rounded-full flex items-center justify-center text-sm">DR</div>
        <div className="text-right">
          <div className="font-semibold">Dr. Rodriguez</div>
          <div className="text-sm opacity-80">Veterinario</div>
        </div>
      </div>
    </header>
  );
};

export default Header;
