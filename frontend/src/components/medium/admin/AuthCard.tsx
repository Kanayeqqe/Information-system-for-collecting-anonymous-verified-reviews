import Button from "../../small/button/button";
import Card from "../../small/card/card";
import Input from "../../small/input/input";

export default function AuthCard() {
	return (
		<Card className="w-152.5 h-78 flex flex-col gap-4">
			<div className="space-y-1">
				<h1 className="text-[19px]">Авторизация получателя</h1>
				<p className="text-[14px] text-t-muted">Введите уникальный UUID и токен владельца</p>
			</div>
			<Input w="full" placeholder="Введите UUID-код" />
			<Input w="full" placeholder="Введите Token-код" />
			<Button text="Продолжить" w="full" />
		</Card>
	)
}