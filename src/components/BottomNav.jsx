import { NavLink, useLocation } from 'react-router-dom';
import { CalendarIcon, HomeIcon, NewsIcon } from './Icons';

const tabs = [
  { to: '/', label: 'Home', Icon: HomeIcon, end: true },
  { to: '/schedule', label: 'Schedule', Icon: CalendarIcon },
  { to: '/news', label: 'News', Icon: NewsIcon },
];

export default function BottomNav() {
  const { pathname } = useLocation();
  // Game preview is a pushed screen with its own back link.
  if (pathname.startsWith('/game/')) return null;
  return (
    <nav aria-label="Main" className="bottom-nav">
      {tabs.map((tab) => {
        const Icon = tab.Icon;
        return (
          <NavLink key={tab.to} to={tab.to} end={tab.end} className="nav-tab">
            <Icon />
            {tab.label}
          </NavLink>
        );
      })}
    </nav>
  );
}
