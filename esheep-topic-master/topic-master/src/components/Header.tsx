import React from 'react';
import { Sun, Moon, Laptop, Languages } from 'lucide-react';
import { ThemeMode } from '../App';
import { Language, translations } from '../i18n';

interface HeaderProps {
  themeMode: ThemeMode;
  lang: Language;
  onThemeModeChange: (mode: ThemeMode) => void;
  onLangToggle: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  themeMode,
  lang,
  onThemeModeChange,
  onLangToggle,
}) => {
  const t = translations[lang];

  const cycleTheme = () => {
    if (themeMode === 'light') onThemeModeChange('dark');
    else if (themeMode === 'dark') onThemeModeChange('system');
    else onThemeModeChange('light');
  };

  const getThemeLabel = () => {
    switch (themeMode) {
      case 'light': return t.themeLight;
      case 'dark': return t.themeDark;
      case 'system': return t.themeSystem;
    }
  };

  return (
    <header className="bg-[#fff8f6] dark:bg-[#201f1f] shadow-sm flex justify-between items-center w-full px-4 md:px-12 py-3.5 mx-auto z-10 sticky top-0 border-b border-[#f5ded6] dark:border-[#353534] transition-colors">
      {/* Brand Title */}
      <div className="flex items-center gap-3">
        <span className="font-extrabold text-2xl md:text-3xl text-[#ff5f00] dark:text-[#ffb599] tracking-tight font-heading">
          Topic Master
        </span>
      </div>

      {/* Control Buttons (Language Toggle on the left, Theme Mode on the right) */}
      <div className="flex items-center gap-2.5">
        {/* Language Switch Button */}
        <button
          onClick={onLangToggle}
          title={`Language: ${lang === 'zh' ? '中文 (Click for English)' : 'English (点击切换为中文)'}`}
          className="px-3 py-2 bg-[#f5ded6] dark:bg-[#2a2a2a] text-[#251914] dark:text-[#e5e2e1] rounded-lg shadow-ambient hover:scale-95 transition-transform border border-transparent dark:border-[#353534] cursor-pointer flex items-center gap-1.5 font-bold text-xs"
        >
          <Languages className="w-4 h-4 text-[#ff5f00] dark:text-[#ffb599]" />
          <span>{lang === 'zh' ? '中 / EN' : 'EN / 中'}</span>
        </button>

        {/* Theme Mode Toggle Button */}
        <button
          onClick={cycleTheme}
          title={`${t.themeLight}/${t.themeDark}: ${getThemeLabel()}`}
          className="p-2.5 bg-[#f5ded6] dark:bg-[#2a2a2a] text-[#251914] dark:text-[#e5e2e1] rounded-lg shadow-ambient hover:scale-95 transition-transform border border-transparent dark:border-[#353534] cursor-pointer flex items-center justify-center"
        >
          {themeMode === 'light' && <Sun className="w-4 h-4 text-amber-700" />}
          {themeMode === 'dark' && <Moon className="w-4 h-4 text-[#ffb599]" />}
          {themeMode === 'system' && <Laptop className="w-4 h-4 text-amber-700 dark:text-[#ffb599]" />}
        </button>
      </div>
    </header>
  );
};
