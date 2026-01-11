import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Color } from 'three';

const BackgroundMesh = () => {
    const mesh = useRef<any>(null);
    const uniforms = useMemo(
        () => ({
            uTime: { value: 0 },
            uColor1: { value: new Color('#1e1b4b') }, // deep indigo
            uColor2: { value: new Color('#4c1d95') }, // violet
            uColor3: { value: new Color('#0f172a') }, // slate 900
        }),
        []
    );

    useFrame((state) => {
        if (mesh.current) {
            mesh.current.material.uniforms.uTime.value = state.clock.getElapsedTime();
        }
    });

    return (
        <mesh ref={mesh}>
            <planeGeometry args={[2, 2]} />
            <shaderMaterial
                fragmentShader={`
                    uniform float uTime;
                    uniform vec3 uColor1;
                    uniform vec3 uColor2;
                    uniform vec3 uColor3;

                    varying vec2 vUv;

                    void main() {
                        vec2 uv = vUv;
                        
                        // Create a flowing, organic gradient pattern
                        float t = uTime * 0.15;
                        
                        float noise1 = sin(uv.x * 3.0 + t) * cos(uv.y * 2.5 - t);
                        float noise2 = cos(uv.x * 4.0 - t * 1.5) * sin(uv.y * 5.0 + t);
                        
                        float mixRatio = (noise1 + noise2) * 0.25 + 0.5;
                        
                        vec3 finalColor = mix(uColor3, uColor1, uv.y);
                        finalColor = mix(finalColor, uColor2, mixRatio * 0.6);
                        
                        // Add some subtle grain/dither
                        float grain = fract(sin(dot(uv, vec2(12.9898, 78.233))) * 43758.5453);
                        finalColor += grain * 0.02;

                        gl_FragColor = vec4(finalColor, 1.0);
                    }
                `}
                vertexShader={`
                    varying vec2 vUv;
                    void main() {
                        vUv = uv;
                        gl_Position = vec4(position, 1.0);
                    }
                `}
                uniforms={uniforms}
            />
        </mesh>
    );
};

const ShaderBackground = () => {
    return (
        <div className="fixed inset-0 z-[-1] pointer-events-none">
            <Canvas camera={{ position: [0, 0, 1] }}>
                <BackgroundMesh />
            </Canvas>
        </div>
    );
}

export default ShaderBackground;
