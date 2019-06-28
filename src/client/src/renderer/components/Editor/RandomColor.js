/**
 * @module RandomColor
 * @desc Generates a random color based on a seed
 */
import Color from 'color'
// Mixed array of the numbers 0 to 360 to make the colors appear more random.
// 169is the coprime of 360, thus all numbers generated are unique.
const pearsonTable = [...new Array(360)].map((_, i) => i * 169 % 360)

/**
 * Generates a color based on the seed. It disregards numbers and underscores.
 * @param {string} seed a string
 * @returns {Object} a color object
 */
export function getRandomColor (seed) {
  const hue = seed.replace(/[0-9]/g, '').replace(/_/g, '').split('').reduce((hash, char) => {
    return pearsonTable[(hash + char.charCodeAt(0)) % (pearsonTable.length - 1)]
  }, seed.length % (pearsonTable.length - 1))
  return Color.hsl(hue, 90, 50)
}
