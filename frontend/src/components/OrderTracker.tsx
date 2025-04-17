import React, { useEffect, useState } from 'react';
import { WebSocket } from 'ws';

interface OrderStatus {
    status: string;
    estimatedTime: number;
    currentStep: string;
    driverLocation?: {
        lat: number;
        lng: number;
    };
}

interface OrderTrackerProps {
    orderId: string;
    customerId: string;
    onStatusChange?: (status: OrderStatus) => void;
}

export const OrderTracker: React.FC<OrderTrackerProps> = ({
    orderId,
    customerId,
    onStatusChange
}) => {
    const [status, setStatus] = useState<OrderStatus | null>(null);
    const [ws, setWs] = useState<WebSocket | null>(null);

    useEffect(() => {
        const websocket = new WebSocket(
            `ws://localhost:8000/ws/order-tracking/${orderId}`
        );

        websocket.onmessage = (event) => {
            const newStatus = JSON.parse(event.data);
            setStatus(newStatus);
            onStatusChange?.(newStatus);
        };

        setWs(websocket);

        return () => {
            websocket.close();
        };
    }, [orderId]);

    const renderStatusStep = (step: string, isActive: boolean) => (
        <div className={`status-step ${isActive ? 'active' : ''}`}>
            <div className="step-indicator"></div>
            <div className="step-label">{step}</div>
        </div>
    );

    return (
        <div className="order-tracker">
            <h3>Pedido #{orderId}</h3>
            
            <div className="status-timeline">
                {renderStatusStep('Orden Recibida', 
                    status?.currentStep === 'received')}
                {renderStatusStep('En Preparación', 
                    status?.currentStep === 'preparing')}
                {renderStatusStep('En Camino', 
                    status?.currentStep === 'delivering')}
                {renderStatusStep('Entregado', 
                    status?.currentStep === 'delivered')}
            </div>

            {status?.estimatedTime && (
                <div className="estimated-time">
                    Tiempo estimado: {status.estimatedTime} minutos
                </div>
            )}

            {status?.driverLocation && (
                <div className="driver-location">
                    <h4>Ubicación del Repartidor</h4>
                    <div className="map-container">
                        {/* Add your preferred map component here */}
                    </div>
                </div>
            )}
        </div>
    );
}; 