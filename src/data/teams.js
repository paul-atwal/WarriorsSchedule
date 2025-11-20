export const teamDetails = {
  'Los Angeles Lakers': {
    record: '10-5',
    scorers: [
      { name: 'LeBron James', ppg: 25.4, img: 'https://cdn.nba.com/headshots/nba/latest/1040x760/2544.png' },
      { name: 'Anthony Davis', ppg: 24.8, img: 'https://cdn.nba.com/headshots/nba/latest/1040x760/203076.png' },
      { name: 'Austin Reaves', ppg: 16.2, img: 'https://cdn.nba.com/headshots/nba/latest/1040x760/1630559.png' },
    ],
    h2h: [
      { date: 'Oct 20, 2025', score: '115-109', result: 'W' },
    ]
  },
  'San Antonio Spurs': {
    record: '8-8',
    scorers: [
      { name: 'Victor Wembanyama', ppg: 22.5, img: 'https://cdn.nba.com/headshots/nba/latest/1040x760/1641705.png' },
      { name: 'Devin Vassell', ppg: 19.1, img: 'https://cdn.nba.com/headshots/nba/latest/1040x760/1630170.png' },
      { name: 'Keldon Johnson', ppg: 17.4, img: 'https://cdn.nba.com/headshots/nba/latest/1040x760/1629640.png' },
    ],
    h2h: []
  },
  'Brooklyn Nets': {
    record: '6-10',
    scorers: [
      { name: 'Mikal Bridges', ppg: 21.2, img: 'https://cdn.nba.com/headshots/nba/latest/1040x760/1628969.png' },
      { name: 'Cam Thomas', ppg: 20.5, img: 'https://cdn.nba.com/headshots/nba/latest/1040x760/1630560.png' },
      { name: 'Nic Claxton', ppg: 12.8, img: 'https://cdn.nba.com/headshots/nba/latest/1040x760/1629651.png' },
    ],
    h2h: []
  },
  'Miami Heat': {
    record: '9-7',
    scorers: [
      { name: 'Jimmy Butler', ppg: 23.6, img: 'https://cdn.nba.com/headshots/nba/latest/1040x760/202710.png' },
      { name: 'Bam Adebayo', ppg: 20.1, img: 'https://cdn.nba.com/headshots/nba/latest/1040x760/1628389.png' },
      { name: 'Tyler Herro', ppg: 19.8, img: 'https://cdn.nba.com/headshots/nba/latest/1040x760/1629639.png' },
    ],
    h2h: []
  },
  'Denver Nuggets': {
    record: '12-4',
    scorers: [
      { name: 'Nikola Jokic', ppg: 28.9, img: 'https://cdn.nba.com/headshots/nba/latest/1040x760/203999.png' },
      { name: 'Jamal Murray', ppg: 21.5, img: 'https://cdn.nba.com/headshots/nba/latest/1040x760/1627750.png' },
      { name: 'Michael Porter Jr.', ppg: 17.2, img: 'https://cdn.nba.com/headshots/nba/latest/1040x760/1629008.png' },
    ],
    h2h: [
        { date: 'Nov 5, 2025', score: '108-112', result: 'L' }
    ]
  },
  // Fallback for others
  'default': {
    record: '0-0',
    scorers: [
      { name: 'Player One', ppg: 20.0, img: 'https://via.placeholder.com/150' },
      { name: 'Player Two', ppg: 18.0, img: 'https://via.placeholder.com/150' },
      { name: 'Player Three', ppg: 15.0, img: 'https://via.placeholder.com/150' },
    ],
    h2h: []
  }
};
