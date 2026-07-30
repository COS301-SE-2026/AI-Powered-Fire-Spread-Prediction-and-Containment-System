'use client';

import React, {useEffect, useRef} from 'react';

// Ember particle system adapted from:
// Cheney Lin, "Fire Embers by Html5 Canvas", CodePen.
// https://codepen.io/CheneyLin/pen/ZmaxNG

export default function EmberField() {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let ww = canvas.width = canvas.offsetWidth;
        let wh = canvas.height = canvas.offsetHeight;

        function between(min: number, max: number) {
            return Math.random() * (max - min) + min;
        }

        interface Particle {
            x: number;
            y: number;
            size: number;
            vx: number;
            vy: number;
            g: number;
            life: number;
            color: string;
            reset: () => void;
        }

        function createP(): Particle {
            const p = {} as Particle;

            const setup = () => {
                p.x = between(ww * 0.1, ww * 0.9);
                p.y = between(wh * 0.9, wh * 1);

                p.size = Math.random() * 2.5;

                p.vx = Math.random() * 1 - 0.5;
                p.vy = between(-0.5, -0.75);

                p.g = -0.001 * Math.random() * 10;

                p.life = between(wh / 2, wh);

                const colors = ['#FF4904', '#fe8024', '#fcba3e'];
                p.color = colors[Math.floor(Math.random() * colors.length)];
            };
            setup();
            p.reset = setup;
            return p;
        }    

    const particles: Particle[] = Array.from({length: 25}, createP);

    let rafId: number;
    const draw = () => {
        ctx.clearRect(0, 0, ww, wh);

        for (const p of particles) {
            ctx.beginPath();
            ctx.fillStyle = p.color;
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();

            p.x += p.vx;
            p.y += p.vy += p.g;

            p.life--;

            if (p.life < 25) p.color = '#3d1a0f';
            if (p.life < 1) p.reset();
        }
        rafId = requestAnimationFrame(draw);
    };
    draw();

    return () => cancelAnimationFrame(rafId);
}, []);

return (
    <canvas ref={canvasRef} className='pointer-events-none absolute inset-0 w-ful h-full' aria-hidden="true" />
);
}