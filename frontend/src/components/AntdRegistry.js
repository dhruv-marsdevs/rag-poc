"use client";

import React from "react";
import { StyleProvider, createCache, extractStyle } from "@ant-design/cssinjs";
import { useServerInsertedHTML } from "next/navigation";

export default function AntdRegistry({ children }) {
	const cache = React.useMemo(() => createCache(), []);

	useServerInsertedHTML(() => {
		return (
			<style
				id="antd"
				dangerouslySetInnerHTML={{ __html: extractStyle(cache, true) }}
			/>
		);
	});

	return (
		<StyleProvider
			cache={cache}
			hashPriority="high"
		>
			{children}
		</StyleProvider>
	);
}
