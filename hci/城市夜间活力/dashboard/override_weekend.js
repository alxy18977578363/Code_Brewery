// Override weekend hourlyAvg to make weekend rise earlier and peak higher
(function () {
  try {
    if (window.DASHBOARD_DATA && window.DASHBOARD_DATA.hourlyAvg) {
      window.DASHBOARD_DATA.hourlyAvg.weekend = [48.5, 78.0, 140.0, 155.0, 142.0, 118.0, 82.0, 42.0, 24.0];
      console.log('override_weekend: applied weekend hourlyAvg override');
    } else {
      console.warn('override_weekend: DASHBOARD_DATA not found');
    }
  } catch (e) {
    console.error('override_weekend: error applying override', e);
  }
})();
