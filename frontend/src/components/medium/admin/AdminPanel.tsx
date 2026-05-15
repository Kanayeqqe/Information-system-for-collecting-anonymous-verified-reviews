import Button from "../../small/button/button";
import Card from "../../small/card/card";

export default function AdminPanel() {
	return (
		<div className="w-screen h-screen p-6 text-white grid grid-cols-[250px_1fr] gap-4">
			<Card className="h-full flex flex-col gap-3">
				<Button text="Статистика" w="full" />
				<Button text="Информация о боксе" w="full" />
				<Button text="UUID-ссылки" w="full" />
				<Button text="Отзывы" w="full" />
			</Card>

			<div className="h-full grid grid-rows-[120px_1fr_250px] gap-4">

				<div className="grid grid-cols-3 gap-4">
					<Card className="h-full"> </Card>
					<Card className="h-full"> </Card>
					<Card className="h-full"> </Card>
				</div>

				<div className="grid grid-cols-2 gap-4">
					<Card className="h-full">
						<h2 className="text-[17px] font-normal mb-2">Последние отзывы</h2>
					</Card>
					<Card className="h-full">
						<h2 className="text-[17px] font-normal mb-2">UUID-ссылки</h2>
					</Card>
				</div>

				<div className="grid grid-cols-[1.5fr_1fr] gap-4">
					<Card className="h-full">
						<h2 className="text-[17px] font-normal mb-2">Динамика активности</h2>
						{/* график */}
					</Card>
					<Card className="h-full">
						<h2 className="text-[17px] font-normal mb-2">Состояние системы</h2>
					</Card>
				</div>

			</div>
		</div>
	);
}