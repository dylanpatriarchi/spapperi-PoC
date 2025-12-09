'use client';

import { Canvas } from '@react-three/fiber';
import { Environment, OrbitControls, useGLTF, Float, Stage } from '@react-three/drei';
import { Suspense } from 'react';

function Model() {
    const { scene } = useGLTF('/machine.glb');
    return <primitive object={scene} />;
}

export default function Scene() {
    return (
        <div className="w-full h-full">
            <Canvas shadows dpr={[1, 2]} camera={{ position: [4, 2, 5], fov: 45 }}>
                <Suspense fallback={null}>
                    <Stage environment="city" intensity={0.6}>
                        <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
                            <Model />
                        </Float>
                    </Stage>
                </Suspense>
                <OrbitControls
                    autoRotate
                    autoRotateSpeed={0.8}
                    enableZoom={false}
                    enablePan={false}
                    minPolarAngle={Math.PI / 4}
                    maxPolarAngle={Math.PI / 2}
                />
            </Canvas>
        </div>
    );
}
