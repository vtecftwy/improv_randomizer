export interface BubblePos {
  x: number
  y: number
}

/** Reference window height (px) the Tkinter sizes were designed for. */
const REF_HEIGHT = 960

/**
 * Bubble centres on an ellipse (1.5x wider than tall), starting at 12 o'clock and going clockwise.
 * Same geometry as GameSpace.draw_games, where radius = 280/960 of the window height.
 */
export function bubbleLayout(count: number, canvasW: number, canvasH: number, windowH: number): BubblePos[] {
  const cx = canvasW / 2
  const cy = canvasH / 2
  const r = (280 / REF_HEIGHT) * windowH
  const step = (2 * Math.PI) / count
  return Array.from({ length: count }, (_, i) => ({
    x: cx + r * Math.sin(step * i) * 1.5,
    y: cy - r * Math.cos(step * i),
  }))
}

/** Scale factor for bubble size and font relative to the original 55px-radius bubbles. */
export const bubbleScale = (windowH: number) => windowH / 1040
