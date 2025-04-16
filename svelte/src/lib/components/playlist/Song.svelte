<script>
	let { data } = $props();
</script>

<div
	class="flex items-center justify-between bg-back-grey rounded py-2 px-3 my-2 transition-transform hover:scale-105 duration-200"
>
	<p class="font-medium text-white">{data[0]}</p>
	<p class="text-sm text-gray-300">{data[1]}</p>
</div>
