import React from 'react';
import { Search, Plus, Sun, Moon, Laptop, X } from 'lucide-react';
import { ThemeMode } from '../App';

interface HeaderProps {
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  selectedCategory: string;
  setSelectedCategory: (cat: string) => void;
  categories: string[];
  themeMode: ThemeMode;
  onThemeModeChange: (mode: ThemeMode) => void;
  onOpenNewTopic: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  searchQuery,
  setSearchQuery,
  selectedCategory,
  setSelectedCategory,
  categories,
  themeMode,
  onThemeModeChange,
  onOpenNewTopic,
}) => {
  const cycleTheme = () => {
    if (themeMode === 'light') onThemeModeChange('dark');
    else if (themeMode === 'dark') onThemeModeChange('system');
    else onThemeModeChange('light');
  };

  const getThemeLabel = () => {
    switch (themeMode) {
      case 'light': return 'Light';
      case 'dark': return 'Dark';
      case 'system': return 'System';
    }
  };

  return (
    <header className="bg-[#fff8f6] dark:bg-[#201f1f] shadow-sm flex flex-wrap justify-between items-center w-full px-4 md:px-12 py-3.5 mx-auto z-10 sticky top-0 border-b border-[#f5ded6] dark:border-[#353534] gap-3 transition-colors">
      {/* Brand Title */}
      <div className="flex items-center gap-3">
        <span className="font-extrabold text-2xl md:text-3xl text-[#ff5f00] dark:text-[#ffb599] tracking-tight font-heading">
          Topic Master
        </span>
      </div>

      {/* Controls & Action Buttons */}
      <div className="flex items-center flex-wrap gap-2.5">
        {/* Search Input */}
        <div className="relative min-w-[200px] sm:w-64">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search topics..."
            className="w-full pl-3.5 pr-9 py-2 bg-white dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm transition-all"
          />
          {searchQuery ? (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-2.5 text-[#5b4137] hover:text-[#251914] dark:text-[#e4bfb1]"
            >
              <X className="w-4 h-4" />
            </button>
          ) : (
            <Search className="w-4 h-4 absolute right-3 top-2.5 text-[#5b4137]/70 dark:text-[#e4bfb1]/70" />
          )}
        </div>

        {/* Category Filter Dropdown */}
        {categories.length > 0 && (
          <div className="relative hidden lg:block">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 bg-white dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm focus:outline-none"
            >
              <option value="All">All Categories</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Theme Mode Toggle Button (Light / Dark / System) */}
        <button
          onClick={cycleTheme}
          title={`Current Mode: ${getThemeLabel()} (Click to switch)`}
          className="flex items-center gap-1.5 px-3 py-2 bg-[#f5ded6] dark:bg-[#2a2a2a] text-[#251914] dark:text-[#e5e2e1] rounded-lg shadow-ambient hover:scale-95 transition-transform border border-transparent dark:border-[#353534] cursor-pointer text-xs font-semibold"
        >
          {themeMode === 'light' && <Sun className="w-4 h-4 text-amber-700" />}
          {themeMode === 'dark' && <Moon className="w-4 h-4 text-[#ffb599]" />}
          {themeMode === 'system' && <Laptop className="w-4 h-4 text-blue-600 dark:text-blue-400" />}
          <span className="hidden sm:inline">{getThemeLabel()}</span>
        </button>

        {/* New Topic Button */}
        <button
          onClick={onOpenNewTopic}
          className="bg-[#ff5f00] text-white px-4 py-2 rounded-lg font-semibold text-xs sm:text-sm border-b-2 border-[#a63b00] shadow-ambient hover:scale-[0.98] active:scale-95 transition-all flex items-center gap-1.5 cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span className="whitespace-nowrap">New Topic</span>
        </button>
      </div>
    </header>
  );
};
