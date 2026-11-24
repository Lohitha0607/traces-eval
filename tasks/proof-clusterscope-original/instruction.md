The repository is at `/workspace/clusterscope`. Resolve this GitHub issue:

# Support returning memory data in GigaBytes in `clusterscope.mem`

## Description
Currently, `clusterscope.mem()` returns memory information for the nodes, but there is no built-in mechanism to specify the unit of the returned value (e.g., explicitly requesting Gigabytes vs Megabytes).

I would like to request a feature that adds support for unit conversion directly within the `clusterscope.mem` function.

## Proposed Change
Please add a `to_unit` argument to the `clusterscope.mem()` function.

*   **Argument Name:** `to_unit`
*   **Supported Values:** `"MB"`, `"GB"`
*   **Default Behavior:** It would be convenient if the function could default to `"GB"`, or at least support it as an option.
*   **Error Handling:** If a user provides a unit that is not supported (e.g., `"TB"`), the function should raise a `ValueError` listing the currently supported units.

## Example Usage
Here is the desired workflow for this feature:

```python
>>> import clusterscope
>>> # Retrieve memory in Gigabytes
>>> clusterscope.mem(to_unit="GB")
1836

>>> # Retrieve memory in Megabytes
>>> clusterscope.mem(to_unit="MB")
1836476

>>> # Attempting to use an unsupported unit
>>> clusterscope.mem(to_unit="TB")
Traceback (most recent call last):
  ...
ValueError: TB is not a supported unit. Currently supported units: MB, GB
```