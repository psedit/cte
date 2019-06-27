import Color from 'color'
// Mixed array of the numbers 0 to 360 to make the colors appear more random.
// 169is the coprime of 360, thus all numbers generated are unique.
const pearsonTable = [...new Array(360)].map((_, i) => i * 169 % 360)

// Peason hash to generate hue
export function getRandomColor (seed) {
  const hue = seed.replace(/[0-9]/g, '').replace(/_/g, '').split('').reduce((hash, char) => {
    return pearsonTable[(hash + char.charCodeAt(0)) % (pearsonTable.length - 1)]
  }, seed.length % (pearsonTable.length - 1))
  return Color.hsl(hue, 90, 50)
}
