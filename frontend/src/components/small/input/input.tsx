interface InputProps {
    placeholder?: string;
    w?: "full" | "fit";
    className?: string;
}

export default function Input({
    placeholder = "Введите текст...",
    w = "fit",
    className = ""
}: InputProps) {
    const fontStyles = "text-white font-normal text-[15px] placeholder:text-gray-400"
    const baseStyles = "bg-ui-card p-2 pl-4 pt-3 pb-3` border-ui-border border-1 rounded-[10px] opacity-100 outline-none focus:border-blue-500 transition-colors"
    const width = w === "full" ? "w-full" : "w-fit"

    return (
        <input
            type="text"
            placeholder={placeholder}
            className={`${width} ${baseStyles} ${fontStyles} ${className}`}
        />
    )
}
