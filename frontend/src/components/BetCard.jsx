import React from 'react';
const BetCard = ({ game }) => {
  return (
    <div>
      <h3>{game?.home_team} vs {game?.away_team}</h3>
      <p>Odds: {game?.odds || 'N/A'}</p>
    </div>
  );
};
export default BetCard;
