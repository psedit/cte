import Color from 'color'
const pearsonTable = [...new Array(360)].map((_, i) => i).sort(() => 0.5 - Math.random())

// Peason hash to generate hue
export function getRandomColor (seed) {
  const hue = seed.split('').reduce((hash, char) => {
    return pearsonTable[(hash + char.charCodeAt(0)) % (pearsonTable.length - 1)]
  }, seed.length % (pearsonTable.length - 1))
  return Color.hsl(hue, 90, 50)
}
