import { HtmlHTMLAttributes, ReactNode } from "react";
interface CardProps extends HtmlHTMLAttributes<HTMLDivElement> {
    children: ReactNode;
}
export default function Card({ children, className = "", ...props }: CardProps) {
    return (
        <div
            className={`bg-ui-card text-white p-6 border border-ui-border rounded-xl ${className}`}
            {...props}
        >
            {children}
        </div>
    )
}