import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Shape, ExtrudeGeometry, Group } from 'three';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Cpu, ShieldCheck, Layers, Zap } from "lucide-react";

// Box Component
interface BoxProps {
    position: [number, number, number];
    rotation: [number, number, number];
}

const Box: React.FC<BoxProps> = ({ position, rotation }) => {
    const shape = new Shape();
    const angleStep = Math.PI * 0.5;
    const radius = 1;

    shape.absarc(2, 2, radius, angleStep * 0, angleStep * 1);
    shape.absarc(-2, 2, radius, angleStep * 1, angleStep * 2);
    shape.absarc(-2, -2, radius, angleStep * 2, angleStep * 3);
    shape.absarc(2, -2, radius, angleStep * 3, angleStep * 4);

    const extrudeSettings = {
        depth: 0.3,
        bevelEnabled: true,
        bevelThickness: 0.05,
        bevelSize: 0.05,
        bevelSegments: 20,
        curveSegments: 20
    };

    const geometry = new ExtrudeGeometry(shape, extrudeSettings);
    geometry.center();

    return (
        <mesh
            geometry={geometry}
            position={position}
            rotation={rotation}
        >
            <meshPhysicalMaterial
                color="#6d28d9" // Matching primary-700
                metalness={0.8}
                roughness={0.2}
                reflectivity={0.9}
                ior={1.5}
                emissive="#4c1d95" // primary-900
                emissiveIntensity={0.2}
                transparent={true} // Allow transparency
                opacity={0.7}      // Show shader through
                transmission={0.4}
                thickness={0.5}
                clearcoat={1.0}
                clearcoatRoughness={0.1}
                sheen={0.5}
                sheenRoughness={0.5}
                sheenColor="#ffffff"
                specularIntensity={1.0}
                specularColor="#ffffff"
            />
        </mesh>
    );
};

// AnimatedBoxes Component
const AnimatedBoxes: React.FC = () => {
    const groupRef = useRef<Group>(null);

    useFrame((_state, delta) => {
        if (groupRef.current) {
            groupRef.current.rotation.x += delta * 0.05;
        }
    });

    const boxes = Array.from({ length: 50 }, (_, index) => ({
        position: [(index - 25) * 0.75, 0, 0] as [number, number, number],
        rotation: [
            (index - 10) * 0.1,
            Math.PI / 2,
            0
        ] as [number, number, number],
        id: index
    }));

    return (
        <group ref={groupRef}>
            {boxes.map((box) => (
                <Box
                    key={box.id}
                    position={box.position}
                    rotation={box.rotation}
                />
            ))}
        </group>
    );
};

// Scene Component
export const Scene: React.FC = () => {
    // Fixed camera position
    const cameraPosition: [number, number, number] = [5, 5, 20];

    return (
        <div className="w-full h-full z-0 p-0 m-0 absolute inset-0 pointer-events-none">
            <Canvas camera={{ position: cameraPosition, fov: 40 }} gl={{ alpha: true }}>
                <ambientLight intensity={10} />
                <directionalLight position={[10, 10, 5]} intensity={10} color="#c084fc" />
                <AnimatedBoxes />
            </Canvas>
        </div>
    );
};

// Features Data
const features = [
    {
        icon: Cpu,
        title: "AI-Powered RAG",
        description: "Intelligent retrieval augmented generation for accurate answers.",
    },
    {
        icon: ShieldCheck,
        title: "Secure Processing",
        description: "Your documents are processed locally and securely.",
    },
    {
        icon: Layers,
        title: "Multi-Format Support",
        description: "PDFs, DOCX, Text, and URLs - we handle it all.",
    },
    {
        icon: Zap,
        title: "Instant Answers",
        description: "Get immediate responses from your custom knowledge base.",
    },
];

// Hero Section Component
interface HeroSectionProps {
    onGetStarted: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onGetStarted }) => {
    return (
        <div className="min-h-screen w-full text-white flex flex-col items-center justify-center px-8 pt-32 pb-8 relative overflow-hidden">
            {/* We do NOT add a background here so the ShaderBackground shows through */}

            <div className="w-full max-w-6xl space-y-12 relative z-10">
                <div className="flex flex-col items-center text-center space-y-8 animate-fade-in-up">
                    <Badge variant="secondary" className="backdrop-blur-md bg-white/10 border border-white/20 text-white hover:bg-white/20 px-4 py-2 rounded-full">
                        ✨ Next Generation Q&A
                    </Badge>

                    <div className="space-y-6 flex items-center justify-center flex-col w-full">
                        <h1 className="text-3xl sm:text-4xl md:text-7xl font-bold tracking-tight max-w-4xl drop-shadow-2xl bg-gradient-to-r from-white to-primary-100 bg-clip-text text-transparent px-4">
                            DocuMind: AI-Powered Document Intelligence
                        </h1>
                        <p className="text-base md:text-xl text-primary-100/80 max-w-2xl font-light px-6">
                            Transform any document into an intelligent knowledge base. Ask questions, get instant answers powered by advanced RAG technology.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 items-center pt-4 w-full justify-center px-8">
                            <Button
                                onClick={onGetStarted}
                                className="w-full sm:w-auto text-base md:text-lg px-8 py-6 rounded-2xl bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 text-white font-bold shadow-[0_0_20px_rgba(139,92,246,0.5)] transform hover:-translate-y-1 hover:scale-105 transition-all duration-300 border border-white/10"
                            >
                                Get Started
                            </Button>
                            <Button
                                variant="outline"
                                className="text-sm md:text-base px-5 md:px-8 py-3 md:py-5 rounded-2xl border-white/20 hover:bg-white/10 text-white backdrop-blur-md"
                            >
                                Learn More
                            </Button>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 max-w-5xl mx-auto pt-10">
                    {features.map((feature, idx) => (
                        <div
                            key={idx}
                            className="group backdrop-blur-md bg-white/5 hover:bg-white/10 border border-white/10 hover:border-primary-500/50 rounded-2xl p-6 flex flex-col justify-start items-start space-y-4 transition-all duration-300 hover:-translate-y-1"
                        >
                            <div className="p-2 rounded-lg bg-primary-500/20 group-hover:bg-primary-500/30 transition-colors">
                                <feature.icon size={24} className="text-primary-200 group-hover:text-white" />
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold text-white mb-1">{feature.title}</h3>
                                <p className="text-sm text-slate-300 leading-relaxed">{feature.description}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className='absolute inset-0 z-0 opacity-50 pointer-events-none'>
                <Scene />
            </div>


        </div>
    );
};
