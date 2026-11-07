// Global variables
const SIZE = 900
const CENTER = SIZE / 2
const RADIUS = 200
const TILT = 0.38
const FRAME_MS = 50
const OCEAN = 9000
const CLOUDS = 3200
const SPECKS = 520
const RINGS = 10
const RING_DOTS = 300
const SHADES = 10
const { abs, asin, atan2, cos, hypot, PI, random, sin, sqrt } = Math

type Vector = [number, number, number]
type Ground = { at: Vector, isLand: boolean }
type Speck = { angle: number, reach: number, height: number, speed: number }
type Ring = { tilt: number, turn: number, speed: number, moon: number | null }
type Layer = number[][]
type Scene = { ground: Ground[], clouds: Vector[], lines: Vector[],
    specks: Speck[], rings: Ring[] }

let context: CanvasRenderingContext2D | null = null
let scene: Scene | null = null
let frame = 0
let drawn = 0


// Code
/** Turn the globe on or off; with reduced motion it stays on one frame. */
export function showGlobe({ on }: { on: boolean }): void {

    cancelAnimationFrame(frame)

    if (!on) return

    const canvas = document.querySelector<HTMLCanvasElement>('#globe')

    if (!canvas) return

    if (!context) context = prepare({ canvas })

    if (!scene) scene = build()

    if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
        draw({ context, scene, time: 0 })
        return
    }

    const painter = context
    const world = scene

    const loop = (time: number): void => {
        frame = requestAnimationFrame(loop)

        // A slow globe looks smooth at 20 frames and leaves time for typing
        if (time - drawn < FRAME_MS || !canvas.checkVisibility()) return

        drawn = time
        draw({ context: painter, scene: world, time })
    }

    frame = requestAnimationFrame(loop)
}

/** Size the canvas for this screen and get its drawing context. */
function prepare({ canvas }: {
    canvas: HTMLCanvasElement,
}): CanvasRenderingContext2D {

    const ratio = Math.min(devicePixelRatio, 2)
    canvas.width = SIZE * ratio
    canvas.height = SIZE * ratio
    const drawing = canvas.getContext('2d')!
    drawing.scale(ratio, ratio)

    return drawing
}

/** Spread points evenly over a ball, keeping the ones `keep` accepts. */
function ball({ count, keep }: {
    count: number,
    keep: (latitude: number, longitude: number) => boolean,
}): Vector[] {

    const golden = PI * (3 - sqrt(5))
    const points: Vector[] = []

    for (let i = 0; i < count; i++) {
        const y = 1 - (i / (count - 1)) * 2
        const width = sqrt(1 - y * y)
        const x = cos(golden * i) * width
        const z = sin(golden * i) * width

        if (keep(asin(y), atan2(z, x))) points.push([x, y, z])
    }

    return points
}

/** Tell whether a place of the ball is land, by summing a few waves. */
function isOverLand(latitude: number, longitude: number): boolean {

    const wave = sin(longitude * 2 + 0.5) * cos(latitude * 1.5) * 0.9
        + sin(longitude * 5 + latitude * 3 + 1.7) * 0.45
        + cos(latitude * 6 - longitude * 3 + 0.4) * 0.35
        + sin(longitude * 11 + latitude * 7) * 0.18

    return wave > 0.42 || abs(latitude) > 1.22
}

/** Tell whether a place of the ball has a cloud over it. */
function isCloud(latitude: number, longitude: number): boolean {

    const wave = sin(longitude * 4 + latitude * 5 + 2.1) * 0.6
        + cos(longitude * 9 - latitude * 4) * 0.4
        + sin(latitude * 12 + longitude * 2) * 0.25

    return wave > 0.62
}

/** Make the dotted parallels and meridians. */
function gridLines(): Vector[] {

    const lines: Vector[] = []
    const onBall = (latitude: number, longitude: number): Vector => [
        cos(latitude) * cos(longitude),
        sin(latitude),
        cos(latitude) * sin(longitude),
    ]

    for (let degrees = -60; degrees <= 60; degrees += 30) {

        for (let k = 0; k < 160; k++) {
            lines.push(onBall(degrees * PI / 180, k / 160 * PI * 2))
        }
    }

    for (let degrees = 0; degrees < 360; degrees += 30) {

        for (let k = 0; k < 80; k++) {
            lines.push(onBall((k / 80 - 0.5) * PI, degrees * PI / 180))
        }
    }

    return lines
}

/** Compute once everything that the frames only rotate. */
function build(): Scene {

    const ground = ball({ count: OCEAN, keep: () => true }).map(at => {

        return { at, isLand: isOverLand(asin(at[1]), atan2(at[2], at[0])) }
    })
    const specks = Array.from({ length: SPECKS }, () => ({
        angle: random() * PI * 2,
        reach: 1.15 + random() * 0.75,
        height: (random() - 0.5) * 0.5,
        speed: 0.00008 + random() * 0.00022,
    }))
    const rings = Array.from({ length: RINGS }, (_, i) => ({
        tilt: (i + 0.5) / RINGS * PI,
        turn: i * 2.39996,
        speed: (i % 2 ? -1 : 1) * (0.1 + 0.03 * (i % 4)),
        moon: i % 3 === 0 ? i * 0.7 : null,
    }))
    const clouds = ball({ count: CLOUDS, keep: isCloud })

    return { ground, clouds, lines: gridLines(), specks, rings }
}

/** Rotate a point by `angle`, tilt it and place it on the canvas. */
function project({ point, angle }: { point: Vector, angle: number }): Vector {

    const [x, y, z] = point
    const turnedX = x * cos(angle) + z * sin(angle)
    const turnedZ = -x * sin(angle) + z * cos(angle)
    const tiltedY = y * cos(TILT) - turnedZ * sin(TILT)
    const depth = y * sin(TILT) + turnedZ * cos(TILT)

    return [CENTER + turnedX * RADIUS, CENTER - tiltedY * RADIUS, depth]
}

/** Find where a ring passes at `angle`, already on the canvas. */
function onRing({ ring, angle }: { ring: Ring, angle: number }): Vector {

    const reach = 1.38
    const x = cos(angle) * reach
    const z = sin(angle) * reach
    const y = -z * sin(ring.tilt)
    const lifted = z * cos(ring.tilt)
    const point: Vector = [
        x * cos(ring.turn) + lifted * sin(ring.turn),
        y,
        -x * sin(ring.turn) + lifted * cos(ring.turn),
    ]

    return project({ point, angle: 0 })
}

/** Tell whether a point is behind the ball. */
function isHidden(point: Vector): boolean {

    const distance = hypot(point[0] - CENTER, point[1] - CENTER)

    return point[2] < 0 && distance < RADIUS
}

/** Paint the glow around the ball and the ball itself. */
function drawBall({ context, time }: {
    context: CanvasRenderingContext2D,
    time: number,
}): void {

    const breath = sin(time * 0.0009)
    const glow = context.createRadialGradient(
        CENTER, CENTER, RADIUS * 0.95,
        CENTER, CENTER, RADIUS * (1.32 + 0.05 * breath),
    )
    glow.addColorStop(0, `rgb(90 160 255 / ${0.15 + 0.04 * breath})`)
    glow.addColorStop(1, 'rgb(90 160 255 / 0)')
    context.fillStyle = glow
    context.fillRect(0, 0, SIZE, SIZE)

    const light = CENTER - RADIUS * 0.35
    const body = context.createRadialGradient(
        light, light, RADIUS * 0.1,
        CENTER, CENTER, RADIUS,
    )
    body.addColorStop(0, 'rgb(70 130 230 / 0.45)')
    body.addColorStop(1, 'rgb(6 12 40 / 0.85)')
    context.fillStyle = body
    context.beginPath()
    context.arc(CENTER, CENTER, RADIUS, 0, PI * 2)
    context.fill()
}

/** Make an empty set of dots, one list for each brightness. */
function newLayer(): Layer {

    return Array.from({ length: SHADES + 1 }, () => [])
}

/** Put a dot in the list of its brightness. */
function add({ layer, x, y, alpha }: {
    layer: Layer,
    x: number,
    y: number,
    alpha: number,
}): void {

    layer[Math.round(alpha * SHADES)].push(x, y)
}

/** Paint a layer, setting each color once, the slow step of the canvas. */
function paint({ context, layer, color, size }: {
    context: CanvasRenderingContext2D,
    layer: Layer,
    color: string,
    size: number,
}): void {

    layer.forEach((dots, shade) => {
        context.fillStyle = `rgb(${color} / ${shade / SHADES})`

        for (let i = 0; i < dots.length; i += 2) {
            context.fillRect(dots[i], dots[i + 1], size, size)
        }
    })
}

/** Paint the front of the ball: grid, land, sea and clouds. */
function drawSurface({ context, scene, angle }: {
    context: CanvasRenderingContext2D,
    scene: Scene,
    angle: number,
}): void {

    const lines = newLayer()
    const land = newLayer()
    const sea = newLayer()
    const clouds = newLayer()

    for (const point of scene.lines) {
        const [x, y, z] = project({ point, angle })

        if (z > 0) add({ layer: lines, x, y, alpha: 0.2 })
    }

    for (const { at, isLand } of scene.ground) {
        const [x, y, z] = project({ point: at, angle })

        if (z <= 0) continue

        if (isLand) add({ layer: land, x, y, alpha: 0.3 + 0.7 * z })
        else add({ layer: sea, x, y, alpha: 0.1 + 0.1 * z })
    }

    for (const cloud of scene.clouds) {
        const point = cloud.map(part => part * 1.03) as Vector
        const [x, y, z] = project({ point, angle: angle * 1.35 })

        if (z > 0) add({ layer: clouds, x, y, alpha: 0.18 + 0.4 * z })
    }

    paint({ context, layer: lines, color: '120 180 255', size: 1 })
    paint({ context, layer: sea, color: '60 120 220', size: 1.2 })
    paint({ context, layer: land, color: '165 212 255', size: 2.1 })
    paint({ context, layer: clouds, color: '235 245 255', size: 2.4 })
}

/** Paint a moon with its glow. */
function drawMoon({ context, moon }: {
    context: CanvasRenderingContext2D,
    moon: Vector,
}): void {

    context.shadowBlur = 22
    context.shadowColor = '#bfe3ff'
    context.fillStyle = '#fff'
    context.beginPath()
    context.arc(moon[0], moon[1], 3.6, 0, PI * 2)
    context.fill()
    context.shadowBlur = 0
}

/** Paint the dust, the rings and their moons around the ball. */
function drawOrbit({ context, scene, time }: {
    context: CanvasRenderingContext2D,
    scene: Scene,
    time: number,
}): void {

    const dust = newLayer()
    const rings = newLayer()

    for (const speck of scene.specks) {
        const angle = speck.angle + time * speck.speed
        const point: Vector = [
            cos(angle) * speck.reach,
            speck.height,
            sin(angle) * speck.reach,
        ]
        const placed = project({ point, angle: 0 })
        const [x, y, z] = placed

        if (!isHidden(placed)) {
            add({ layer: dust, x, y, alpha: z > 0 ? 0.5 : 0.2 })
        }
    }

    for (const ring of scene.rings) {
        const phase = time * 0.0006 * ring.speed

        for (let k = 0; k < RING_DOTS; k++) {
            const angle = k / RING_DOTS * PI * 2 + phase
            const placed = onRing({ ring, angle })

            if (k % 7 <= 4 && !isHidden(placed)) {
                add({ layer: rings, x: placed[0], y: placed[1], alpha: 0.3 })
            }
        }
    }

    paint({ context, layer: dust, color: '120 185 255', size: 1.6 })
    paint({ context, layer: rings, color: '140 190 255', size: 1.3 })

    for (const ring of scene.rings) {

        if (ring.moon === null) continue

        const angle = ring.moon + time * 0.001 * ring.speed
        const moon = onRing({ ring, angle })

        if (!isHidden(moon)) drawMoon({ context, moon })
    }
}

/** Paint one frame of the globe. */
function draw({ context, scene, time }: {
    context: CanvasRenderingContext2D,
    scene: Scene,
    time: number,
}): void {

    context.globalCompositeOperation = 'source-over'
    context.clearRect(0, 0, SIZE, SIZE)
    drawBall({ context, time })
    context.globalCompositeOperation = 'lighter'
    drawSurface({ context, scene, angle: time * 0.00022 })
    drawOrbit({ context, scene, time })
}
