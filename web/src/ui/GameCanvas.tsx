import { useEffect, useRef, useState } from 'react'
import type { Game } from '../engine/types'
import { bubbleLayout, bubbleScale } from './bubbleLayout'
import type { GameView } from './useGameSession'

interface Props {
  games: Game[]
  view: GameView
  backgroundUrl: string
}

// Footer (50) + header (1) + canvas margin (100) in the Tkinter layout.
const CHROME_H = 151

export function GameCanvas({ games, view, backgroundUrl }: Props) {
  const ref = useRef<HTMLDivElement>(null)
  const [size, setSize] = useState({ w: 800, h: 600 })

  useEffect(() => {
    const el = ref.current!
    const ro = new ResizeObserver(([e]) => setSize({ w: e.contentRect.width, h: e.contentRect.height }))
    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  const { w, h } = size
  const windowH = h + CHROME_H
  const s = bubbleScale(windowH)
  const pos = bubbleLayout(games.length, w, h, windowH)
  const rx = 75 * s
  const ry = 55 * s

  return (
    <div className="canvas" ref={ref}>
      <svg viewBox={`0 0 ${w} ${h}`}>
        <image href={backgroundUrl} x={0} y={0} width={w} height={h} preserveAspectRatio="xMidYMid slice" />
        {pos.map((p, i) => (
          <line key={`l${i}`} x1={w / 2} y1={h / 2} x2={p.x} y2={p.y} stroke="var(--cyan)" strokeWidth={1} />
        ))}
        {pos.map((p, i) => {
          const current = view.currentIdx === i || view.spinningIdx === i
          const played = view.playedIdxs.includes(i)
          const fill = current ? 'var(--flashy-green)' : played ? 'var(--dark-green)' : 'var(--cyan)'
          return (
            <g key={games[i].name + i}>
              <ellipse cx={p.x} cy={p.y} rx={rx} ry={ry} fill={fill} stroke="var(--blue)" strokeWidth={1} />
              <foreignObject x={p.x - rx * 0.8} y={p.y - ry} width={rx * 1.6} height={ry * 2}>
                <div className={`bubble-label${played && !current ? ' played' : ''}`} style={{ fontSize: 15 * s }}>
                  {games[i].name}
                </div>
              </foreignObject>
            </g>
          )
        })}
      </svg>
    </div>
  )
}
